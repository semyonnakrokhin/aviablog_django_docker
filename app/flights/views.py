from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.forms import modelformset_factory
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, CreateView, FormView, UpdateView, DeleteView
from .forms import AddFlightForm, MealForm, TrackImageForm, UserTripForm
from .permissions import IsOwnerPermissionMixin
from .services import FlightInformationService, PassengerService, PassengerProfileService, FlightDetailService

from .models import *
from pprint import pprint


class HomeView(ListView):
    template_name = 'flights/index.html'
    queryset = FlightInformationService.get_latest_cards()
    context_object_name = 'latest_cards'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_users'] = FlightInformationService.get_top_users()
        context['site_information'] = FlightInformationService.get_site_information()

        return context


class PassengersView(ListView):
    template_name = 'flights/passengers.html'
    context_object_name = 'passengers'
    queryset = PassengerService.get_all_passengers_with_statistic()


class ProfileView(DetailView):
    template_name = 'flights/profile.html'
    slug_field = 'passenger__username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flights'] = PassengerProfileService.get_passenger_flights(self.kwargs['username'])

        return context

    def get_object(self):
        return PassengerProfileService.get_profile_information(self.kwargs['username'])


class FlightView(DetailView):
    template_name = 'flights/flight.html'
    slug_url_kwarg = 'usertripslug'
    context_object_name = 'flight'

    def get_object(self):
        data, files, _ = FlightDetailService.get_flight_details(self.kwargs['usertripslug'])
        return {**data, **files}


class FlightDeleteView(IsOwnerPermissionMixin, DeleteView):
    # form_class = AddFlightForm
    # formset_class = modelformset_factory(TrackImage, form=TrackImageForm, fields=('track_img',), extra=10)
    form_class = UserTripForm
    success_url = reverse_lazy('home')
    slug_url_kwarg = 'usertripslug'
    queryset = UserTrip.objects.all()

    def get_passenger(self):
        data, _, _ = FlightDetailService.get_flight_details(self.kwargs['usertripslug'])
        return data.get('user')

    # def post(self, request, usertripslug):
    #     data, files, id_dict = FlightDetailService.get_flight_details(usertripslug)
    #     track_images = data.get('track_images')
    #
    #     form = self.form_class(None, None)
    #
    #     with transaction.atomic():
    #         print('form acts')
    #         form.save(user=request.user, **id_dict)
    #
    #         # for track_image_instance in track_images:
    #         #     track_image_instance.delete()
    #
    #     return redirect('home')


class FlightUpdateView(IsOwnerPermissionMixin, View):
    template_name = 'flights/add_flight.html'
    form_class = AddFlightForm
    formset_class = modelformset_factory(TrackImage, form=TrackImageForm, fields=('track_img',), extra=10)

    def get_passenger(self):
        data, _, _ = FlightDetailService.get_flight_details(self.kwargs['usertripslug'])
        return data.get('user')

    def get(self, request, usertripslug):
        data, files, _ = FlightDetailService.get_flight_details(usertripslug)

        formset = self.formset_class(queryset=data.get('track_images'))
        form = self.form_class(initial={**data, **files})

        context = {
            'form': form,
            'formset': formset,
            'title': 'Edit Flight',
            'view_name': 'flight_update',
            'url_args': usertripslug
        }
        return render(request, self.template_name, context=context)

    def get_files(self, request, usertripslug: str):
        '''In case a field has an image uploaded and we want to delete it by checking 'clear'-box
        we need to delete this image from request.FILES (actually collect new dict 'files' where there is no this image)
        because with case is not processed by Django automatically (Or I couldn't find how to do this).
        Image deletion is in form class'''

        _, files, __ = FlightDetailService.get_flight_details(usertripslug)

        files_copy = files.copy()
        for field_name, file in files_copy.items():
            if (field_name + '-clear') in request.POST:
                files.pop(field_name)

        files.update(request.FILES.dict())
        return files

    def post(self, request, usertripslug):
        _, __, id_dict = FlightDetailService.get_flight_details(usertripslug)

        form = self.form_class(data=request.POST, files=self.get_files(request, usertripslug))
        formset = self.formset_class(request.POST or None, request.FILES or None)

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():
                # Обновляется вся информация, которая есть по всем id-шникам
                trip = form.save(user=request.user, **id_dict)

                for index, f in enumerate(formset):
                    if f.cleaned_data:

                        if f.cleaned_data.get('id') is None:
                            # Мы загрузили новое изображение в форму

                            track_image_instance = TrackImage(trip=trip, track_img=f.cleaned_data.get('track_img'))
                            track_image_instance.save()
                        elif f.cleaned_data.get('track_img') is False:
                            # Мы поставили галочку напротив очистить
                            id = f.cleaned_data.get('id').id

                            track_image_instance = TrackImage.objects.get(pk=id)
                            track_image_instance.delete()
                        else:
                            # Если изображение было загружено ранее (то есть у него уже есть id в бд)
                            id = f.cleaned_data.get('id').id

                            track_image_instance_in_db = TrackImage.objects.get(pk=id)
                            track_image_instance_in_db.track_img = \
                                TrackImage(trip=trip, track_img=f.cleaned_data.get('track_img')).track_img
                            track_image_instance_in_db.save()

            return redirect('flight', usertripslug=usertripslug)

        context = {
            'title': 'Edit Flight',
            'form': form,
            'formset': formset,
            'view_name': 'flight_update',
            'url_args': usertripslug
        }
        return render(request, self.template_name, context=context)


class AddFlightView(LoginRequiredMixin, FormView):
    form_class = AddFlightForm
    formset_class = modelformset_factory(TrackImage, form=TrackImageForm, fields=('track_img',), extra=10)
    template_name = 'flights/add_flight.html'
    success_url = reverse_lazy('home')

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_valid(self, form, formset):
        with transaction.atomic():
            trip = form.save(user=self.request.user)
            for f in formset:
                if f.cleaned_data:
                    track_image_instance = f.save(trip=trip)
                    track_image_instance.save()

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        formset = self.formset_class(request.POST or None, request.FILES or None)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = 'add_flight'
        context['url_args'] = ''
        context['title'] = 'Add New Flight'
        context['formset'] = self.formset_class(queryset=TrackImage.objects.none())
        return context
