import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django

django.setup()

from flights.models import AircraftType, Airline, Airframe, Flight
from django.test import TestCase, override_settings
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from aviablog import settings
import shutil
import tempfile
from datetime import time

tmp_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
            airline=cls.airline,
        )

        cls.flight = Flight.objects.create(
            flight_number='KJC542',
            airframe=cls.airframe,
            date='2023-07-26',
            flight_time=time(hour=3, minute=45),
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


tmp_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=tmp_dir)
class AirframeTest(TestCase):

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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(cls.media_root)

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


@override_settings(MEDIA_ROOT=tmp_dir)
class FLightTest(TestCase):

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
            airline=cls.airline,
        )

    def test_delete_primary_model_instance(self):
        flight = Flight.objects.create(
            flight_number='KJC542',
            airframe=self.airframe,
            date='2023-07-26',
            flight_time=time(hour=3, minute=45),
        )

        flight_db = Flight.objects.get(pk=flight.pk)
        airframe_db = flight_db.airframe

        self.assertEqual(airframe_db.flight_set.count(), 1)

        flight_db.delete()

        self.assertFalse(Flight.objects.filter(pk=flight.pk).exists())
        self.assertFalse(Airframe.objects.filter(pk=flight.airframe.id).exists())

    def test_no_delete_primary_model_instance(self):
        flight1 = Flight.objects.create(
            flight_number='KJC542',
            airframe=self.airframe,
            date='2023-07-26',
            flight_time=time(hour=3, minute=45),
        )

        flight2 = Flight.objects.create(
            flight_number='ABC123',
            airframe=self.airframe,
            date='2023-07-27',
            flight_time=time(hour=4, minute=30),
        )

        flight1_db = Flight.objects.get(pk=flight1.pk)
        flight2_db = Flight.objects.get(pk=flight1.pk)
        airframe1_db = flight1_db.airframe
        airframe2_db = flight2_db.airframe

        self.assertEqual(airframe1_db, airframe2_db)

        self.assertEqual(airframe1_db.flight_set.count(), 2)

        flight1_db.delete()

        self.assertFalse(Flight.objects.filter(pk=flight1.pk).exists())
        self.assertTrue(Flight.objects.filter(pk=flight2.pk).exists())
        self.assertTrue(Airframe.objects.filter(pk=flight1.airframe.id).exists())

    def test_unique_together_constraint(self):
        flight1 = Flight.objects.create(
            flight_number='KJC542',
            airframe=self.airframe,
            date='2023-07-26',
            flight_time=time(hour=3, minute=45),
        )

        with self.assertRaises(Exception) as context:
            flight2 = Flight.objects.create(
                flight_number=flight1.flight_number,
                airframe=flight1.airframe,
                date=flight1.date,
                flight_time=flight1.flight_time,
            )

        self.assertIsInstance(context.exception, IntegrityError)

    def test_airframe_null(self):
        flight = Flight.objects.create(
            flight_number='KJC542',
            airframe=None,
            date='2023-07-26',
            flight_time='03:45',
        )

        self.assertTrue(Flight.objects.filter(pk=flight.pk).exists())
        self.assertIsNone(flight.airframe)


class UserTripTest(TestCase):
    pass
