import os
from datetime import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django

django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import pre_save, post_delete

from flights.models import Airframe, TrackImage, Meal, Airline, UserTrip, Flight
from flights.tests.tests_model import Settings
from django.contrib.auth import get_user_model

UserClass = get_user_model()


class SettingsMixin(Settings):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.track_image = TrackImage.objects.create(
            trip=cls.usertrip,
            track_img=SimpleUploadedFile('track-01.jpg', b"file_content")
        )

        cls.meal = Meal.objects.create(
            trip=cls.usertrip,
            drinks='Вода и соки',
            meal_price=340,
            meal_photo=SimpleUploadedFile('meal-01.jpg', b"file_content")
        )


class PreSavePhotoDeleteSignalHandlerTest(SettingsMixin):

    def test_delete_previous_photo_airframe(self):
        new_airframe = Airframe(
            pk=self.airframe.pk,
            serial_number='SN67890',
            registration_number='RA-24680',
            photo=SimpleUploadedFile("new_test.jpg", b"new_file_content"),
            aircraft_type=self.aircraft_type,
            airline=self.airline
        )

        pre_save.send(sender=Airframe, instance=new_airframe)

        self.assertFalse(self.airframe.photo.storage.exists(self.airframe.photo.name))

    def test_delete_previous_photo_meal(self):
        new_meal = Meal(
            pk=self.meal.pk,
            trip=self.usertrip,
            drinks='Вино',
            appertize='Салат зимний',
            main_course='Говядина с картошкой',
            desert='Шоколадный мусс',
            meal_price=340,
            meal_photo=SimpleUploadedFile('new_meal.jpg', b"file_content")
        )
        pre_save.send(sender=Meal, instance=new_meal)

        self.assertFalse(self.meal.meal_photo.storage.exists(self.meal.meal_photo.name))

    def test_delete_previous_photo_trackimage(self):
        new_track_image = TrackImage(
            pk=self.track_image.pk,
            trip=self.usertrip,
            track_img=SimpleUploadedFile('new_track-xx.jpg', b"file_content")
        )
        pre_save.send(sender=TrackImage, instance=new_track_image)

        self.assertFalse(self.track_image.track_img.storage.exists(self.track_image.track_img.name))


class PostDeleteImageSignalHandlerTest(SettingsMixin):

    @staticmethod
    def get_common_directory(start_directory, finish_directory):
        current_path = start_directory
        media_root = finish_directory

        while current_path != media_root:
            if os.path.isdir(current_path):
                contents = os.listdir(current_path)
                if len(contents) > 1:
                    return current_path

            current_path = os.path.dirname(current_path)

        return current_path

    def test_delete_not_alone_airframe(self):
        airframe2 = Airframe.objects.create(
            serial_number='SN67890',
            registration_number='RA-24680',
            photo=SimpleUploadedFile("new_airframe2.jpg", b"new_file_content"),
            aircraft_type=self.aircraft_type,
            airline=self.airline
        )

        self.assertEqual(airframe2.airline.name, self.airline.name)
        expected_directory = os.path.join(self.media_root, 'airframes', self.airline.name).lower()
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 2)

        post_delete.send(sender=Airframe, instance=airframe2)

        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

    def test_delete_alone_airframe(self):
        airline = Airline.objects.create(
            name='AirUnion'
        )

        airframe2 = Airframe.objects.create(
            serial_number='SN77777',
            registration_number='RA-75467',
            photo=SimpleUploadedFile("new_airframe2.jpg", b"new_file_content"),
            aircraft_type=self.aircraft_type,
            airline=airline
        )

        expected_directory = os.path.join(self.media_root, 'airframes', airframe2.airline.name)
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

        expected_directory_after_delete = self.get_common_directory(expected_directory, os.path.join(self.media_root))

        _, folder_path = post_delete.send(sender=Airframe, instance=airframe2)[0]

        self.assertEqual(expected_directory_after_delete, folder_path)

    def test_delete_not_alone_meal(self):
        meal2 = Meal.objects.create(
            trip=self.usertrip,
            drinks='Вино',
            appertize='Салат морковный',
            main_course='Рыба',
            desert='Шоколадный мусс',
            meal_price=340,
            meal_photo=SimpleUploadedFile('new_meal.jpg', b"file_content")
        )

        expected_directory = os.path.join(
            self.media_root,
            'meal',
            meal2.trip.flight.flight_number,
            meal2.trip.flight.date
        ).lower()
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 2)

        post_delete.send(sender=Meal, instance=meal2)

        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

    def test_delete_alone_meal(self):

        flight = Flight.objects.create(
            flight_number='AFL1450',
            airframe=self.airframe,
            date='2021-10-21',
            flight_time=time(hour=3, minute=45),
        )

        usertrip = UserTrip.objects.create(
            flight=flight,
            passenger=self.user
        )

        meal2 = Meal.objects.create(
            trip=usertrip,
            drinks='Вино',
            appertize='Салат морковный',
            main_course='Рыба',
            desert='Шоколадный мусс',
            meal_price=340,
            meal_photo=SimpleUploadedFile('new_meal.jpg', b"file_content")
        )

        expected_directory = os.path.join(
            self.media_root,
            'meal',
            meal2.trip.flight.flight_number,
            meal2.trip.flight.date
        ).lower()
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

        expected_directory_after_delete = self.get_common_directory(expected_directory, os.path.join(self.media_root))

        _, folder_path = post_delete.send(sender=Meal, instance=meal2)[0]

        self.assertEqual(expected_directory_after_delete, folder_path.lower())

    def test_delete_not_alone_track_image(self):
        track_image2 = TrackImage.objects.create(
            trip=self.usertrip,
            track_img=SimpleUploadedFile('track-02.jpg', b"file_content_lalala")
        )

        expected_directory = os.path.join(
            self.media_root,
            'tracks',
            track_image2.trip.passenger.username,
            track_image2.trip.flight.flight_number,
            track_image2.trip.flight.date
        ).lower()
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 2)

        post_delete.send(sender=TrackImage, instance=track_image2)

        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

    def test_delete_alone_track_image(self):

        usertrip = UserTrip.objects.create(
            flight=self.flight,
            passenger=UserClass.objects.create(username='Erdem', password='bachatadancer')
        )

        track_image2 = TrackImage.objects.create(
            trip=usertrip,
            track_img=SimpleUploadedFile('alternative.jpg', b"file_content_lalala")
        )

        expected_directory = os.path.join(
            self.media_root,
            'tracks',
            track_image2.trip.passenger.username,
            track_image2.trip.flight.flight_number,
            track_image2.trip.flight.date
        ).lower()
        self.assertTrue(os.path.exists(expected_directory))
        self.assertEqual(sum([1 for path in os.scandir(expected_directory) if path.is_file()]), 1)

        expected_directory_after_delete = self.get_common_directory(expected_directory, os.path.join(self.media_root))

        _, folder_path = post_delete.send(sender=TrackImage, instance=track_image2)[0]

        self.assertEqual(expected_directory_after_delete, folder_path.lower())
