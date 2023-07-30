import os
from unittest.mock import patch

from django.db.models import QuerySet

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django

django.setup()

from test_mixins import UploadDataMixin
from flights.services import FlightInformationService, PassengerService, PassengerProfileService, FlightDetailService
from flights.models import UserTrip


class FlightInformationServiceTest(UploadDataMixin):

    def test_get_latest_cards(self):

        cards = FlightInformationService.get_latest_cards()

        self.assertIsInstance(cards, list)
        self.assertEqual(len(cards), 6)

        for card in cards:
            self.assertIn('photo_url', card)
            self.assertIn('flight_number', card)
            self.assertIn('date', card)
            self.assertIn('passenger', card)
            self.assertIn('airline', card)
            self.assertIn('aircraft_type', card)
            self.assertIn('departure', card)
            self.assertIn('destination', card)
            self.assertIn('usertripslug', card)

    def test_get_latest_cards_max_count(self):

        cards = FlightInformationService.get_latest_cards(3)

        self.assertIsInstance(cards, list)
        self.assertEqual(len(cards), 3)

    def test_get_latest_cards_empty_queryset(self):
        for ut in UserTrip.objects.all():
            ut.delete()

        cards = FlightInformationService.get_latest_cards()

        self.assertIsInstance(cards, list)
        self.assertEqual(cards, [])

    def test_get_top_users(self):
        top_users = FlightInformationService.get_top_users(3)
        self.assertIsInstance(top_users, QuerySet)
        self.assertEqual(len(top_users), 3)

        for user in top_users:
            self.assertIn('username', user)
            self.assertIn('total_flights', user)

    def test_get_site_information(self):
        site_info = FlightInformationService.get_site_information()
        self.assertIsInstance(site_info, list)
        self.assertEqual(len(site_info), 4)

        expected_titles = ['Unique airlines', 'Unique aircraft types', 'Unique airframes', 'Unique airports']
        expected_values = [7, 7, 7, 14]

        for info, title, value in zip(site_info, expected_titles, expected_values):
            self.assertEqual(info['title'], title)
            self.assertEqual(info['value'], value)


class PassengerServiceTest(UploadDataMixin):

    def test_get_all_passengers_with_statistic(self):
        passengers_data = PassengerService.get_all_passengers_with_statistic()

        self.assertIsInstance(passengers_data, QuerySet)
        self.assertEqual(len(passengers_data), 7)

        for passenger in passengers_data:
            self.assertIn('username', passenger)
            self.assertIn('first_name', passenger)
            self.assertIn('last_name', passenger)
            self.assertIn('total_airlines', passenger)
            self.assertIn('total_aircraft_types', passenger)
            self.assertIn('total_airports', passenger)
            self.assertIn('total_flights', passenger)


class PassengerProfileServiceTest(UploadDataMixin):

    def test_get_profile_information(self):
        profile_info = PassengerProfileService.get_profile_information('test_user_1')

        self.assertIsInstance(profile_info, dict)
        self.assertEqual(profile_info['username'], 'test_user_1')

    def test_get_passenger_flights(self):
        passenger_flights = PassengerProfileService.get_passenger_flights('test_user_1')

        self.assertIsInstance(passenger_flights, QuerySet)
        self.assertTrue(all(hasattr(ut.flight, 'flight_number') for ut in passenger_flights))


class FlightDetailServiceTest(UploadDataMixin):

    def test_get_flight_details(self):

        # Вызов тестируемого метода
        usertripslug = UserTrip.objects.first().slug
        flight_dict, files, id_dict = FlightDetailService.get_flight_details(usertripslug)

        # Проверка утверждений
        self.assertIsInstance(flight_dict, dict)
        self.assertTrue(flight_dict)
        self.assertIsInstance(files, dict)
        self.assertTrue(files)
        self.assertIsInstance(id_dict, dict)
        self.assertTrue(id_dict)

        # Проверяем наличие всех необходимых ключей в словаре flight_dict
        required_keys_flight_dict = [
            'usertripslug',
            'registration_number',
            'serial_number',
            'airline_name',
            'flight_number',
            'date',
            'flight_time',
            'manufacturer',
            'generic_type',
            'aircraft_type',
            'user',
            'seat',
            'neighbors',
            'comments',
            'ticket_price',
            'drinks',
            'appertize',
            'main_course',
            'desert',
            'meal_price',
            'route',
            'departure_info',
            'arrival_info',
            'departure_airport_code',
            'departure_gate',
            'departure_is_boarding_bridge',
            'departure_schedule_time',
            'departure_actual_time',
            'departure_runway',
            'departure_metar',
            'arrival_airport_code',
            'arrival_gate',
            'arrival_is_boarding_bridge',
            'arrival_schedule_time',
            'arrival_actual_time',
            'arrival_runway',
            'arrival_metar',
            'track_images',
        ]
        for key in required_keys_flight_dict:
            self.assertIn(key, flight_dict, f"Key '{key}' not found in flight_dict")

        required_keys_files = files_keys = [
            'airframe_photo',
            'meal_photo',
        ]
        for key in required_keys_files:
            self.assertIn(key, files, f"Key '{key}' not found in files")

        required_keys_id_dict = [
            'usertrip_id',
            'flight_id',
            'meal_id',
            'departure_id',
            'arrival_id',
            'airframe_id',
            'aircraft_type_id',
            'airline_id'
        ]
        for key in required_keys_id_dict:
            self.assertIn(key, id_dict, f"Key '{key}' not found in id_dict")
