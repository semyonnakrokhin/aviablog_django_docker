import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django

django.setup()

from test_mixins import UploadDataMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
from flights.services import PassengerProfileService, FlightDetailService
from django.test import TestCase
from unittest.mock import patch
from flights.factories import UserTripFactory, FlightInfoFactory, MealFactory, TrackImageFactory

from test_mixins.test_data_upload import PostMethodMixin, TemproaryMediaRootMixin
from users.factories import UserFactory

from flights.models import UserTrip, TrackImage
from django.forms import modelformset_factory

from flights.forms import AddFlightForm, TrackImageForm

UserClass = get_user_model()


class HomeViewTest(TemproaryMediaRootMixin):
    def test_latest_cards_displayed(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)

        latest_cards = response.context['latest_cards']
        self.assertIsNotNone(latest_cards)

    def test_top_users_displayed(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        top_users = response.context['top_users']
        self.assertIsNotNone(top_users)

    def test_site_information_displayed(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        site_information = response.context['site_information']
        self.assertIsNotNone(site_information)


class PassengersViewTest(TemproaryMediaRootMixin):
    def test_passengers_displayed(self):
        response = self.client.get(reverse('passengers'))

        self.assertEqual(response.status_code, 200)
        passengers = response.context['passengers']
        self.assertIsNotNone(passengers)


class ProfileViewTest(TemproaryMediaRootMixin, UploadDataMixin):

    def test_flights_displayed(self):
        user = UserClass.objects.first()

        response = self.client.get(reverse('profile', kwargs={'username': user.username}))

        self.assertEqual(response.status_code, 200)
        flights = response.context['flights']
        self.assertIsNotNone(flights)

    @patch('flights.views.PassengerProfileService.get_profile_information')
    def test_profile_information(self, mock_get_profile_information):
        mock_profile_data = {
            'username': 'test_user',
            'first_name': '',
            'last_name': '',
            'total_airlines': 2,
            'total_aircraft_types': 2,
            'total_airports': 1,
            'total_flights': 2
        }
        mock_get_profile_information.return_value = mock_profile_data

        response = self.client.get(reverse('profile', kwargs={'username': 'test_user'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], mock_profile_data)


class FlightViewTest(TemproaryMediaRootMixin, UploadDataMixin):
    def test_flight_detail_object(self):
        usertrip = UserTrip.objects.first()
        response = self.client.get(reverse('flight', kwargs={'usertripslug': usertrip.slug}))

        self.assertEqual(response.status_code, 200)
        flight = response.context['flight']
        self.assertIsNotNone(flight)


class AddFlightViewTest(TemproaryMediaRootMixin, PostMethodMixin):

    def test_create_flight_anonymous(self):
        payload = {
            **self.data,
            **self.files
        }

        response = self.client.post(reverse('add_flight'), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/signup/', response.url)

    def test_create_flight_logined_user(self):
        payload = {
            **self.data,
            **self.files
        }

        test_user = UserFactory()
        self.client.force_login(test_user)

        response = self.client.post(reverse('add_flight'), data=payload)

        usertrip = UserTrip.objects.filter(passenger=test_user)

        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(usertrip)
        self.assertEqual('/', response.url)

    def test_not_valid_data_logined_user(self):
        payload = {
            **self.data
        }

        test_user = UserFactory()
        self.client.force_login(test_user)

        response = self.client.post(reverse('add_flight'), data=payload)

        usertrip = UserTrip.objects.filter(passenger=test_user)

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(usertrip, [])


class FlightUpdateViewTest(TemproaryMediaRootMixin, TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.wrong_user = UserFactory()
        self.usertrip = UserTripFactory()

        FlightInfoFactory(flight=self.usertrip.flight)
        FlightInfoFactory(flight=self.usertrip.flight)
        MealFactory(trip=self.usertrip)
        TrackImageFactory(trip=self.usertrip)

        self.url = reverse("flight_update", kwargs={"usertripslug": self.usertrip.slug})

        self.form_class = AddFlightForm


    # 1) Тестирование метода get, когда пользователь не является владельцем записи
    def test_get_not_owner(self):
        self.client.force_login(self.wrong_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    # 2) Тестирование метода get, когда пользователь является владельцем записи
    def test_get_owner(self):
        self.client.force_login(self.usertrip.passenger)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['title'], 'Edit Flight')
        self.assertEqual(response.context['view_name'], 'flight_update')
        self.assertEqual(response.context['url_args'], self.usertrip.slug)
        self.assertIsInstance(response.context['form'], self.form_class)

    # 3) Тестирование метода get_files
    def test_get_files_clear_yes(self):
        data, files, id_dict = FlightDetailService.get_flight_details(self.usertrip.slug)

        payload = {
            **data,
            'meal_photo-clear': True,
            **files
        }

        response = self.client.post(self.url, data=payload)

        # self.assertEqual(response.status_code, 302)
        # self.assertIsNone(self.usertrip.meal_set.first().meal_photo)

    # 4) Тестирование метода post, когда переданные данные валидны и для formset загружаются новые изображения
    # def test_post_valid_data_with_new_images(self):
    #     # Авторизуем пользователя для тестового клиента
    #     self.client.force_login(self.user)
    #
    #     # Отправляем POST-запрос с валидными данными и новыми изображениями для formset
    #     response = self.client.post(self.url, data=self.data, format="multipart")
    #
    #     # Проверяем, что запрос успешен (статус код 200 или 302)
    #     self.assertIn(response.status_code, [200, 302])
    #
    #     # Проверяем, что объекты в базе данных обновились
    #     updated_usertrip = UserTrip.objects.get(id=self.usertrip.id)
    #     self.assertEqual(updated_usertrip.registration_number, "ABC123")
    #
    #     # Проверяем, что новые изображения были созданы в базе данных
    #     self.assertEqual(updated_usertrip.track_images.count(), 2)  # Предполагаем, что создано два новых изображения
    #
    # # 5) Тестирование метода post, когда переданные данные валидны и для formset поля с изображениями очищаются
    # def test_post_valid_data_with_cleared_images(self):
    #     # Авторизуем пользователя для тестового клиента
    #     self.client.force_login(self.user)
    #
    #     # Добавляем поле для очистки изображения
    #     self.data["form-0-track_img-clear"] = True
    #
    #     # Отправляем POST-запрос с валидными данными и очищенными изображениями для formset
    #     response = self.client.post(self.url, data=self.data, format="multipart")
    #
    #     # Проверяем, что запрос успешен (статус код 200 или 302)
    #     self.assertIn(response.status_code, [200, 302])
    #
    #     # Проверяем, что поля с изображениями были очищены в базе данных
    #     updated_usertrip = UserTrip.objects.get(id=self.usertrip.id)
    #     self.assertFalse(updated_usertrip.track_images.exists())
    #
    # # 6) Тестирование метода post, когда переданные данные валидны и для formset не меняются поля с изображениями
    # def test_post_valid_data_without_changed_images(self):
    #     # Авторизуем пользователя для тестового клиента
    #     self.client.force_login(self.user)
    #
    #     # Убираем поле с изображением из POST-данных
    #     self.data.pop("form-0-track_img")
    #
    #     # Отправляем POST-запрос с валидными данными без изменений для formset
    #     response = self.client.post(self.url, data=self.data, format="multipart")
    #
    #     # Проверяем, что запрос успешен (статус код 200 или 302)
    #     self.assertIn(response.status_code, [200, 302])
    #
    #     # Проверяем, что поля с изображениями в базе данных не изменились
    #     updated_usertrip = UserTrip.objects.get(id=self.usertrip.id)
    #     self.assertEqual(updated_usertrip.track_images.count(), 2)
    #
    # # 7) Тестирование метода post, когда данные невалидны
    # def test_post_invalid_data(self):
    #     # Авторизуем пользователя для тестового клиента
    #     self.client.force_login(self.user)
    #
    #     # Устанавливаем неверные значения для полей данных
    #     self.data["registration_number"] = ""
    #
    #     # Отправляем POST-запрос с невалидными данными
    #     response = self.client.post(self.url, data=self.data, format="multipart")
    #
    #     # Проверяем, что запрос возвращает статус код 200 (ошибка валидации)
    #     self.assertEqual(response.status_code, 200)
    #
    #     # Проверяем, что форма содержит ошибки валидации
    #     self.assertTrue(response.context["form"].errors)
    #
    #     # Проверяем, что сообщение об ошибке отображается на странице
    #     self.assertContains(response, "This field is required.")
