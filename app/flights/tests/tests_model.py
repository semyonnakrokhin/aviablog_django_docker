import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django

django.setup()

from flights.models import AircraftType, Airline, Airframe, Flight, UserTrip, FlightInfo, TrackImage, Meal
from django.test import TestCase, override_settings
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.text import slugify
from aviablog import settings
import shutil
import tempfile
from datetime import time

tmp_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)

UserClass = get_user_model()


@override_settings(MEDIA_ROOT=tmp_dir)
class Settings(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.media_root = tmp_dir

        cls.aircraft_type = AircraftType.objects.create(
            manufacturer='Tupolev',
            generic_type='Tu-154M'
        )
        cls.airline = Airline.objects.create(
            name='KrasAir'
        )

        cls.airframe = Airframe.objects.create(
            serial_number='SN12345',
            registration_number='RA-85729',
            photo=SimpleUploadedFile("test.jpg", b"file_content"),
            aircraft_type=cls.aircraft_type,
            airline=cls.airline
        )

        cls.flight = Flight.objects.create(
            flight_number='KJC542',
            airframe=cls.airframe,
            date='2023-07-26',
            flight_time=time(hour=3, minute=45),
        )

        cls.user = UserClass.objects.create(
            username='test_user',
            email='test_email@mail.ru',
            password='spotting'
        )

        cls.usertrip = UserTrip.objects.create(
            flight=cls.flight,
            passenger=cls.user,
            seat='22D',
            neighbors='xxx',
            comments='yyy',
            price=10000
        )

        cls.flight_info_dep = FlightInfo.objects.create(
            flight=cls.flight,
            status='Departure',
            airport_code='KJA',
            metar='MEATR at KJA',
            gate='9B',
            is_boarding_bridge=True,
            schedule_time="12:30",
            actual_time="13:00",
            runway='29'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(cls.media_root)


class AircraftTypeTest(TestCase):

    def test_unique_instances_ok(self):
        type1 = AircraftType.objects.create(manufacturer='Tupolev', generic_type='Tu-154М')
        type2 = AircraftType.objects.create(manufacturer='Yakovlev', generic_type='Yak-42Д')

        type1_db = AircraftType.objects.get(pk=type1.pk)
        type2_db = AircraftType.objects.get(pk=type2.pk)

        self.assertNotEqual(type1_db.manufacturer, type2_db.manufacturer)
        self.assertNotEqual(type1_db.generic_type, type2_db.generic_type)

    def test_unique_instances_error(self):
        type1 = AircraftType.objects.create(manufacturer='Boeing', generic_type='747')

        with self.assertRaises(Exception) as context:
            type2 = AircraftType.objects.create(manufacturer='Boeing', generic_type='747')

        self.assertIsInstance(context.exception, IntegrityError)


class AirlineTest(TestCase):

    def test_unique_instances_ok(self):
        airline1 = Airline.objects.create(name='KrasAir')
        airline2 = Airline.objects.create(name='SibAviaTrans')

        airline1_db = Airline.objects.get(pk=airline1.pk)
        airline2_db = Airline.objects.get(pk=airline2.pk)

        self.assertNotEqual(airline1_db.name, airline2_db.name)

    def test_unique_instances_error(self):
        airline1 = Airline.objects.create(name='KrasAir')

        with self.assertRaises(Exception) as context:
            airline2 = Airline.objects.create(name='KrasAir')

        self.assertIsInstance(context.exception, IntegrityError)


class AirframeTest(Settings):

    def test_get_airframe_image_path(self):
        expected_path = os.path.join(
            self.media_root,
            'airframes',
            self.airframe.airline.name.lower(),
            self.airframe.registration_number.lower() + '.jpg'
        )

        real_path = Airframe.objects.get(pk=self.airframe.pk).photo.path

        self.assertEqual(expected_path, real_path)

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception) as context:
            airframe2 = Airframe.objects.create(
                serial_number='SN12345',
                registration_number='RA-85729',
                photo=SimpleUploadedFile("test.jpg", b"file_content"),
                aircraft_type=self.aircraft_type,
                airline=self.airline
            )

        self.assertIsInstance(context.exception, IntegrityError)

    def test_photo_required(self):
        with self.assertRaises(ValidationError) as context:
            airframe_without_photo = Airframe(
                serial_number='SN12345',
                registration_number='RA-85730',
                aircraft_type=self.aircraft_type,
                airline=self.airline
            )
            airframe_without_photo.full_clean()

        self.assertIn('photo', context.exception.message_dict)

    def test_aircraft_type_deletion(self):
        aircraft_type = AircraftType.objects.create(
            manufacturer='Test Manufacturer',
            generic_type='Test Generic Type'
        )
        airframe = Airframe.objects.create(
            serial_number='SN12345',
            registration_number='RA-85731',
            photo=SimpleUploadedFile("test.jpg", b"file_content"),
            aircraft_type=aircraft_type,
            airline=self.airline
        )

        aircraft_type.delete()

        all_airframes_of_aircraft_type = Airframe.objects.filter(pk=airframe.pk)
        self.assertTrue(all_airframes_of_aircraft_type.exists())
        self.assertTrue(all(af.aircraft_type is None for af in all_airframes_of_aircraft_type))

    def test_airline_deletion(self):
        airline = Airline.objects.create(
            name='Test Airline'
        )
        airframe = Airframe.objects.create(
            serial_number='SN12345',
            registration_number='RA-85731',
            photo=SimpleUploadedFile("test.jpg", b"file_content"),
            aircraft_type=self.aircraft_type,
            airline=airline
        )
        airline.delete()

        all_airframes_of_airline = Airframe.objects.filter(pk=airframe.pk)
        self.assertTrue(all_airframes_of_airline.exists())
        self.assertTrue(all(af.airline is None for af in all_airframes_of_airline))


class FLightTest(Settings):

    def test_delete_primary_model_instance(self):
        airframe = Airframe.objects.create(
            serial_number='SN3333',
            registration_number='RA-85123',
            photo=SimpleUploadedFile("test.jpg", b"file_content"),
            aircraft_type=self.aircraft_type,
            airline=self.airline,
        )

        flight = Flight.objects.create(
            flight_number='KJC844',
            airframe=airframe,
            date='2023-07-19',
            flight_time=time(hour=2, minute=30),
        )

        flight_db = Flight.objects.get(pk=flight.pk)
        airframe_db = flight_db.airframe

        self.assertEqual(airframe_db.flight_set.count(), 1)

        flight_db.delete()

        self.assertFalse(Flight.objects.filter(pk=flight.pk).exists())
        self.assertFalse(Airframe.objects.filter(pk=airframe.id).exists())

    def test_no_delete_primary_model_instance(self):
        flight1 = self.flight

        flight2 = Flight.objects.create(
            flight_number='ABC123',
            airframe=self.airframe,
            date='2023-07-27',
            flight_time=time(hour=4, minute=30),
        )

        flight1_db = Flight.objects.get(pk=flight1.pk)
        flight2_db = Flight.objects.get(pk=flight2.pk)
        airframe1_db = flight1_db.airframe
        airframe2_db = flight2_db.airframe

        self.assertEqual(airframe1_db, airframe2_db)

        self.assertEqual(airframe1_db.flight_set.count(), 2)

        flight2_db.delete()

        self.assertFalse(Flight.objects.filter(pk=flight2.pk).exists())
        self.assertTrue(Flight.objects.filter(pk=flight1.pk).exists())
        self.assertTrue(Airframe.objects.filter(pk=flight1.airframe.id).exists())

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception) as context:
            flight2 = Flight.objects.create(
                flight_number=self.flight.flight_number,
                airframe=self.flight.airframe,
                date=self.flight.date,
                flight_time=self.flight.flight_time,
            )

        self.assertIsInstance(context.exception, IntegrityError)

    def test_airframe_null(self):
        flight = Flight.objects.create(
            flight_number='KJC444',
            airframe=None,
            date='2023-07-12',
            flight_time='03:45',
        )

        self.assertTrue(Flight.objects.filter(pk=flight.pk).exists())
        self.assertIsNone(flight.airframe)


class UserTripTest(Settings):

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception) as context:
            usertrip2 = UserTrip.objects.create(
                flight=self.usertrip.flight,
                passenger=self.usertrip.passenger,
                seat='1A',
                neighbors='ggg',
                comments='ttt',
                price=5000
            )

        self.assertIsInstance(context.exception, IntegrityError)

    def test_slug_creation(self):
        passenger = UserClass.objects.create(
            username='Nikolay',
            password='Oboroten2000'
        )

        flight = Flight.objects.create(
            flight_number='SBI071',
            airframe=self.airframe,
            date='2020-07-20',
            flight_time=time(hour=3, minute=45),
        )

        expected_slug = slugify(f"{flight.flight_number}-{flight.date}-{passenger.username}")

        usertrip = UserTrip.objects.create(
            flight=flight,
            passenger=passenger,
        )

        usertrip_db = UserTrip.objects.get(pk=usertrip.pk)

        self.assertEqual(usertrip_db.slug, expected_slug)

    def test_delete_primary_model_instance(self):
        airframe = Airframe.objects.create(
            serial_number='SN3333',
            registration_number='RA-85123',
            photo=SimpleUploadedFile("test.jpg", b"file_content"),
            aircraft_type=self.aircraft_type,
            airline=self.airline,
        )

        flight = Flight.objects.create(
            flight_number='KJC844',
            airframe=airframe,
            date='2023-07-19',
            flight_time=time(hour=2, minute=30),
        )

        usertrip = UserTrip.objects.create(
            flight=flight,
            passenger=self.user,
        )

        usertrip_db = UserTrip.objects.get(pk=usertrip.pk)
        flight_db = usertrip_db.flight

        self.assertEqual(flight_db.usertrip_set.count(), 1)

        usertrip_db.delete()

        self.assertFalse(UserTrip.objects.filter(pk=usertrip.pk).exists())
        self.assertFalse(Flight.objects.filter(pk=flight.id).exists())

    def test_no_delete_primary_model_instance(self):
        usertrip1 = self.usertrip

        user2 = UserClass.objects.create(
            username='Nikolay',
            password='Oboroten2000'
        )

        usertrip2 = UserTrip.objects.create(
            flight=self.flight,
            passenger=user2
        )

        usertrip1_db = UserTrip.objects.get(pk=usertrip1.pk)
        usertrip2_db = UserTrip.objects.get(pk=usertrip2.pk)
        flight1_db = usertrip1_db.flight
        flight2_db = usertrip2_db.flight

        self.assertEqual(flight1_db, flight2_db)

        self.assertEqual(flight1_db.usertrip_set.count(), 2)

        usertrip2_db.delete()

        self.assertFalse(UserTrip.objects.filter(pk=usertrip2.pk).exists())
        self.assertTrue(UserTrip.objects.filter(pk=usertrip1.pk).exists())
        self.assertTrue(Flight.objects.filter(pk=usertrip1.flight.id).exists())


class FlightInfoTest(Settings):
    def test_unique_together_constraint(self):
        with self.assertRaises(Exception) as context:
            flight_info_dep_2 = FlightInfo.objects.create(
                flight=self.flight_info_dep.flight,
                airport_code='KJA',
                runway='29'
            )

        self.assertIsInstance(context.exception, IntegrityError)

    def test_creation_error(self):
        with self.assertRaises(Exception) as context:
            flight_info = FlightInfo(
                flight=self.flight_info_dep.flight,
                airport_code='VKO',
            )
            flight_info.full_clean()  # Выполняем валидацию
            flight_info.save()  # Сохранение объекта должно вызвать ошибку валидации

        self.assertIsInstance(context.exception, ValidationError)

    def test_choice_error(self):
        with self.assertRaises(ValidationError) as context:
            flight_info = FlightInfo(
                flight=self.flight_info_dep.flight,
                status='RRR',
                airport_code='DME',
                runway='32L'
            )
            flight_info.full_clean()

        self.assertIsInstance(context.exception, ValidationError)

    def test_choice_ok(self):
        flight_info_departure = FlightInfo.objects.create(
            flight=self.flight_info_dep.flight,
            status='Departure',
            airport_code='DME',
            runway='32L'
        )

        flight_info_arrival = FlightInfo.objects.create(
            flight=self.flight_info_dep.flight,
            status='Arrival',
            airport_code='JFK',
            runway='22R'
        )

        self.assertIsNotNone(flight_info_departure.id)
        self.assertIsNotNone(flight_info_arrival.id)


class TrackImageTest(Settings):
    def test_track_image_path(self):
        filename = "test.jpg"

        track_image = TrackImage.objects.create(
            trip=self.usertrip,
            track_img=SimpleUploadedFile(filename, b"file_content")
        )

        track_image_db = TrackImage.objects.get(pk=track_image.id)

        expected_path = os.path.join(
            self.media_root,
            'tracks',
            str(track_image_db.trip.passenger.username).lower(),
            str(track_image_db.trip.flight.flight_number).lower(),
            str(track_image_db.trip.flight.date),
            filename.lower()
        )

        real_path = track_image_db.track_img.path

        self.assertEqual(expected_path, real_path)

    def test_cascade_delete_of_images(self):
        usertrip = UserTrip.objects.create(
            flight=self.flight,
            passenger=UserClass.objects.create(username='Erdem', password='bachatadancer')
        )

        track_image1 = TrackImage.objects.create(
            trip=usertrip,
            track_img=SimpleUploadedFile("test1.jpg", b"file_content")
        )

        track_image2 = TrackImage.objects.create(
            trip=usertrip,
            track_img=SimpleUploadedFile("test2.jpg", b"file_content")
        )

        usertrip.delete()

        self.assertQuerySetEqual(TrackImage.objects.filter(Q(pk=track_image1.id) | Q(pk=track_image2.id)), [])


class MealTest(Settings):
    def test_meal_image_path(self):
        filename = "meal.jpg"

        meal = Meal.objects.create(
            trip=self.usertrip,
            drinks='Вода и соки',
            meal_price=340,
            meal_photo=SimpleUploadedFile(filename, b"file_content")
        )

        meal_db = Meal.objects.get(pk=meal.id)

        expected_path = os.path.join(
            self.media_root,
            'meal',
            str(meal.trip.flight.flight_number).lower(),
            str(meal.trip.flight.date),
            filename.lower()
        )

        real_path = meal_db.meal_photo.path

        self.assertEqual(expected_path, real_path)

    def test_success_load_without_image(self):
        meal = Meal(
            trip=self.usertrip,
            drinks='Сок',
            appertize='Орешки',
            main_course='Стейк',
            desert='Мороженое',
            meal_price=100
        )

        meal.full_clean()
        meal.save()

        self.assertIsNotNone(meal)

        with self.assertRaises(Exception) as context:
            meal.meal_photo.path

        self.assertIsInstance(context.exception, ValueError)

    def test_cascade_delete_of_meals(self):
        usertrip = UserTrip.objects.create(
            flight=self.flight,
            passenger=UserClass.objects.create(username='Erdem', password='bachatadancer')
        )

        meal1 = Meal.objects.create(
            trip=usertrip,
            drinks='Сок',
            appertize='Орешки',
            main_course='Стейк',
            desert='Мороженое',
            meal_price=100
        )

        meal2 = Meal.objects.create(
            trip=usertrip,
            drinks='Сок',
            appertize='Салат',
            main_course='Запеканка',
            desert='Батончик',
        )

        usertrip.delete()

        self.assertQuerySetEqual(Meal.objects.filter(Q(pk=meal1.id) | Q(pk=meal2.id)), [])
