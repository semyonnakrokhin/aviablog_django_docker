from pprint import pprint
from typing import Union

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.forms import formset_factory

# from users.models import CustomUser
from .models import (Flight,
                     Airline,
                     AircraftType,
                     Airframe,
                     UserTrip,
                     Meal,
                     FlightInfo,
                     TrackImage)


class MyFormMixin:

    @staticmethod
    def get_data_without_files(data: dict):
        data_without_photo = data.copy()

        for key, value in data.items():
            if isinstance(value, InMemoryUploadedFile):
                del data_without_photo[key]

        print(data, data_without_photo, sep='\n')
        return data_without_photo


    def update_create_delete_data(self, model, data: dict, id: Union[int, None]):

        if id is None:
            # Создаем новую запись в бд (либо берем уже существующую, если она присутствует)
            try:
                # Попытка получить запись с использованием урезанного словаря data_without_photo
                instance = model.objects.get(**self.get_data_without_files(data))
            except ObjectDoesNotExist:
                # Создаем новую запись, т.к. в бд нет такой записи
                instance = model.objects.create(**data)

        if id is not None:
            try:
                instance = model.objects.get(pk=id)
                if data:
                    # Обновляем существующую запись. Если словарь data непустой, то это update
                    instance = model(pk=id, **data)
                    instance.save()
                else:
                    # Удаляем существующую запись. Если словарь data пустой, то это delete
                    instance.delete()
            except ObjectDoesNotExist:
                # Запись не найдена
                instance = None

        return instance


class AircraftTypeForm(forms.Form, MyFormMixin):
    manufacturer = forms.CharField(widget=forms.TextInput(attrs={'list': 'manufacturer_choices'}))
    generic_type = forms.CharField(widget=forms.TextInput(attrs={'list': 'generic_type_choices'}))

    def save_aircraft_type(self, aircraft_type_id=None):
        try:
            data_for_aircraft_type = {
                'manufacturer': self.cleaned_data['manufacturer'],
                'generic_type': self.cleaned_data['generic_type']
            }
        except AttributeError:
            data_for_aircraft_type = {}

        return self.update_create_delete_data(AircraftType, data_for_aircraft_type, aircraft_type_id)


class AirlineForm(forms.Form, MyFormMixin):
    airline_name = forms.CharField(label='Airline name',
                                   widget=forms.TextInput(attrs={'list': 'airline_choices'}))

    def save_airline(self, airline_id=None):
        try:
            data_for_airline = {
                'name': self.cleaned_data['airline_name']
            }
        except AttributeError:
            data_for_airline = {}

        return self.update_create_delete_data(Airline, data_for_airline, airline_id)


class AirframeForm(forms.Form, MyFormMixin):
    airframe_photo = forms.ImageField(label='Фото ВС', required=True)
    serial_number = forms.CharField(required=True)
    registration_number = forms.CharField(required=True)

    def save_airframe(self, aircraft_type: AircraftType, airline: Airline, airframe_id=None):
        try:
            data_for_airframe = {
                'serial_number': self.cleaned_data['serial_number'],
                'registration_number': self.cleaned_data['registration_number'],
                'photo': self.cleaned_data['airframe_photo'],
                'aircraft_type': aircraft_type,
                'airline': airline
            }
        except AttributeError:
            data_for_airframe = {}

        return self.update_create_delete_data(Airframe, data_for_airframe, airframe_id)


class FlightForm(forms.Form, MyFormMixin):
    flight_number = forms.CharField(required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    flight_time = forms.TimeField(required=False)

    def save_flight(self, airframe: Airframe, flight_id=None):
        try:
            data_for_flight = {
                'flight_number': self.cleaned_data['flight_number'],
                'date': self.cleaned_data['date'],
                'flight_time': self.cleaned_data['flight_time'],
                'airframe': airframe
            }
        except AttributeError:
            data_for_flight = {}

        return self.update_create_delete_data(Flight, data_for_flight, flight_id)


class UserTripForm(forms.Form, MyFormMixin):
    ticket_price = forms.DecimalField(label='Цена билета', required=False)
    # user = forms.ModelChoiceField(label='Пользователь', queryset=User.objects.all(), required=True)
    seat = forms.CharField(required=False)
    neighbors = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': 70}), required=False)

    def save_user_trip(self, flight: Flight, user: User, usertrip_id=None):
        try:
            data_for_user_trip = {
                'seat': self.cleaned_data['seat'],
                'neighbors': self.cleaned_data['neighbors'],
                'comments': self.cleaned_data['comments'],
                'price': self.cleaned_data['ticket_price'],
                'passenger': user,
                'flight': flight
            }
        except AttributeError:
            data_for_user_trip = {}

        return self.update_create_delete_data(UserTrip, data_for_user_trip, usertrip_id)


class MealForm(forms.Form, MyFormMixin):
    meal_price = forms.DecimalField(label='Цена питания', required=False)
    meal_photo = forms.ImageField(label='Фото питания', required=False)
    drinks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), initial='Вода')
    appertize = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)
    main_course = forms.CharField(widget=forms.Textarea(attrs={'rows': 6, 'cols': 70}), required=False)
    desert = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 70}), required=False)

    def save_meal(self, trip: UserTrip, meal_id=None):
        try:
            data_for_meal = {
                'drinks': self.cleaned_data['drinks'],
                'appertize': self.cleaned_data['appertize'],
                'main_course': self.cleaned_data['main_course'],
                'desert': self.cleaned_data['desert'],
                'meal_price': self.cleaned_data['meal_price'],
                'meal_photo': None if not self.cleaned_data['meal_photo'] else self.cleaned_data['meal_photo'],
                'trip': trip
            }
        except AttributeError:
            data_for_meal = {}

        return self.update_create_delete_data(Meal, data_for_meal, meal_id)


# class FlightInfoForm(forms.Form):
#     status = forms.CharField()
#     airport_code = forms.CharField()
#     metar = forms.CharField()
#     gate = forms.CharField()
#     is_boarding_bridge = forms.BooleanField()
#     schedule_time = forms.TimeField()
#     actual_time = forms.TimeField()
#     runway = forms.CharField()
#
#     def add_prefix(self, field_name):
#         prefix = getattr(self, 'prefix', None)
#         if prefix:
#             return f"{prefix}_{field_name}"
#         return field_name
#
#     def save_flight_info(self, flight: Flight):
#         data_for_flight_info = {
#             'status': self.cleaned_data['status'],
#             'airport_code': self.cleaned_data['airport_code'],
#             'metar': self.cleaned_data['metar'],
#             'gate': self.cleaned_data['gate'],
#             'is_boarding_bridge': self.cleaned_data['is_boarding_bridge'],
#             'schedule_time': self.cleaned_data['schedule_time'],
#             'actual_time': self.cleaned_data['actual_time'],
#             'flight': flight
#         }
#         flight_info_instance, _ = FlightInfo.objects.get_or_create(**data_for_flight_info)
#         return flight_info_instance


# def add_prefix_to_fields(prefix):
#     def decorator(cls):
#         new_fields = {}
#         for field_name, field in cls.base_fields.items():
#             field_name_with_prefix = f"{prefix}_{field_name}"
#             new_fields[field_name_with_prefix] = field
#
#         cls.base_fields = new_fields
#         return cls
#     return decorator
#
#
# @add_prefix_to_fields('departure')
# class DepartureFlightInfoForm(FlightInfoForm, forms.Form):
#     pass

# 'class': 'form-control small-input'
class DepartureFlightInfoForm(forms.Form, MyFormMixin):
    departure_airport_code = forms.CharField(
        label='Airport IATA',
        widget=forms.TextInput(attrs={'placeholder': 'Departure airport'}),
        required=True
    )
    departure_metar = forms.CharField(label='METAR', required=False)
    departure_gate = forms.CharField(label='Gate', required=False)
    departure_is_boarding_bridge = forms.BooleanField(label='Through jet bridge?', required=False)
    departure_schedule_time = forms.TimeField(label='Schedule time', required=False)
    departure_actual_time = forms.TimeField(label='Actual time', required=False)
    departure_runway = forms.CharField(label='Active runway', required=True)

    def save_departure_flight_info(self, flight: Flight, departure_id=None):
        try:
            data_for_flight_info = {
                'status': 'Departure',
                'airport_code': self.cleaned_data['departure_airport_code'],
                'metar': self.cleaned_data['departure_metar'],
                'gate': self.cleaned_data['departure_gate'],
                'is_boarding_bridge': self.cleaned_data['departure_is_boarding_bridge'],
                'schedule_time': self.cleaned_data['departure_schedule_time'],
                'actual_time': self.cleaned_data['departure_actual_time'],
                'runway': self.cleaned_data['departure_runway'],
                'flight': flight
            }
        except AttributeError:
            data_for_flight_info = {}

        return self.update_create_delete_data(FlightInfo, data_for_flight_info, departure_id)


class ArrivalFlightInfoForm(forms.Form, MyFormMixin):
    arrival_airport_code = forms.CharField(
        label='Airport IATA',
        widget=forms.TextInput(attrs={'placeholder': 'Arrival airport'}),
        required=True
    )
    arrival_metar = forms.CharField(label='METAR', required=False)
    arrival_gate = forms.CharField(label='Gate', required=False)
    arrival_is_boarding_bridge = forms.BooleanField(label='Through jet bridge?', required=False)
    arrival_schedule_time = forms.TimeField(label='Schedule time', required=False)
    arrival_actual_time = forms.TimeField(label='Actual time', required=False)
    arrival_runway = forms.CharField(label='Active runway', required=True)

    def save_arrival_flight_info(self, flight: Flight, arrival_id=None):
        try:
            data_for_flight_info = {
                'status': 'Arrival',
                'airport_code': self.cleaned_data['arrival_airport_code'],
                'metar': self.cleaned_data['arrival_metar'],
                'gate': self.cleaned_data['arrival_gate'],
                'is_boarding_bridge': self.cleaned_data['arrival_is_boarding_bridge'],
                'schedule_time': self.cleaned_data['arrival_schedule_time'],
                'actual_time': self.cleaned_data['arrival_actual_time'],
                'runway': self.cleaned_data['arrival_runway'],
                'flight': flight
            }
        except AttributeError:
            data_for_flight_info = {}

        return self.update_create_delete_data(FlightInfo, data_for_flight_info, arrival_id)


class TrackImageForm(forms.ModelForm):
    class Meta:
        model = TrackImage
        fields = '__all__'

    def save(self, trip: UserTrip, commit=False):
        track_image_instance = super().save(commit=False)

        track_image_instance.trip = trip

        if commit:
            track_image_instance.save()

        return track_image_instance


# class TrackImageForm(forms.Form, MyFormMixin):
#     # track_img = forms.ImageField(label='Фото трэка', required=False)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         track_images = self.initial.get('track_images', [])
#
#         if not track_images:  # Создаем одно поле, если нет предыдущих изображений
#             self.fields['track_image_0'] = forms.ImageField(required=False,
#                                                             widget=forms.ClearableFileInput())
#         else:  # Создаем коллекцию полей с предыдущими изображениями
#             for i, image_file in enumerate(track_images):
#                 field_name = f'track_image_{i}'
#                 self.fields[field_name] = forms.ImageField(required=False,
#                                                            initial=image_file,
#                                                            widget=forms.ClearableFileInput())
#
#     def save_track_images(self, trip: UserTrip, track_image_ids: dict):
#         track_image_instances = []
#         track_images_post = {field_name: image
#                              for field_name, image in self.files.items()
#                              if field_name.startswith('track_image_')}
#
#         for track_image_num, image in track_images_post.items():
#
#             track_image_id = track_image_ids.get(track_image_num)
#
#             data_for_track_image = {
#                 'track_img': image,
#                 'trip': trip
#             }
#
#             print(data_for_track_image, track_image_id)
#
#             track_image_instance = self.update_create_delete_data(TrackImage, data_for_track_image, track_image_id)
#
#             track_image_instances.append(track_image_instance)
#
#         return track_image_instances


class AddFlightForm(AircraftTypeForm,
                    AirlineForm,
                    AirframeForm,
                    FlightForm,
                    UserTripForm,
                    MealForm,
                    DepartureFlightInfoForm,
                    ArrivalFlightInfoForm,
                    forms.Form
                    ):

    def save(self, user: User, **kwargs):
        with transaction.atomic():
            aircraft_type_id = kwargs.get('aircraft_type_id')
            airline_id = kwargs.get('airline_id')
            airframe_id = kwargs.get('airframe_id')
            flight_id = kwargs.get('flight_id')
            usertrip_id = kwargs.get('usertrip_id')
            meal_id = kwargs.get('meal_id')
            departure_id = kwargs.get('departure_id')
            arrival_id = kwargs.get('arrival_id')

            # tab1
            aircraft_type_instance = self.save_aircraft_type(aircraft_type_id)
            airline_instance = self.save_airline(airline_id)
            airframe_instance = self.save_airframe(aircraft_type_instance, airline_instance, airframe_id)
            flight_instance = self.save_flight(airframe_instance, flight_id)

            # tab2
            user_trip_instance = self.save_user_trip(flight_instance, user, usertrip_id)

            # tab3
            meal_instance = self.save_meal(user_trip_instance, meal_id)

            # tab4
            departure_flight_info_instance = self.save_departure_flight_info(flight_instance, departure_id)
            arrival_flight_info_instance = self.save_arrival_flight_info(flight_instance, arrival_id)

            # tab5
            # track_image_instances = self.save_track_images(user_trip_instance, track_image_ids)

            return user_trip_instance
