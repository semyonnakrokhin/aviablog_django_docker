import shutil
import tempfile


from django.core.files.uploadedfile import SimpleUploadedFile

from aviablog import settings
from django.test import TestCase, override_settings
from django.core.management import call_command

from flights.factories import UserTripFactory, FlightInfoFactory, MealFactory, TrackImageFactory

from io import BytesIO
from PIL import Image

tmp_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=tmp_dir)
class TemproaryMediaRootMixin(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tmp_dir

        # Вызываем команду flush для очистки базы данных
        call_command('flush', interactive=False)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        # call_command('flush', interactive=False)
        shutil.rmtree(cls.media_root)


class UploadDataMixin(TestCase):
    def setUp(self):
        super().setUp()

        # upload data to db
        usertrip_lst = UserTripFactory.create_batch(7)

        for usertrip in usertrip_lst:
            FlightInfoFactory(flight=usertrip.flight)
            FlightInfoFactory(flight=usertrip.flight)
            MealFactory(trip=usertrip)
            TrackImageFactory(trip=usertrip)


class PostMethodMixin(TestCase):

    def get_image_buffer(self):
        f = BytesIO()
        image = Image.new(mode='RGB', size=(100, 100))
        image.save(f, 'png')
        f.seek(0)
        return f

    def setUp(self):

        self.data = {
            'registration_number': 'ABC123',
            'serial_number': 'XYZ789',
            'airline_name': 'S7 Airlines',

            'flight_number': 'FL123',
            'date': '2023-01-01',
            'flight_time': '12:00',

            'manufacturer': 'Airbus',
            'generic_type': 'A320',

            'seat': 'A1',
            'neighbors': 'B1, C1',
            'comments': 'Test comments',
            'ticket_price': 10000,

            'drinks': 'Test drinks',
            'appertize': 'Test appertize',
            'main_course': 'Test main course',
            'desert': 'Test desert',
            'meal_price': 500,

            'departure_airport_code': 'ABC',
            'departure_gate': 'A',
            'departure_is_boarding_bridge': True,
            'departure_schedule_time': '10:00',
            'departure_actual_time': '10:30',
            'departure_runway': '1',
            'departure_metar': 'METAR data for departure',

            'arrival_airport_code': 'XYZ',
            'arrival_gate': 'B',
            'arrival_is_boarding_bridge': False,
            'arrival_schedule_time': '14:00',
            'arrival_actual_time': '14:15',
            'arrival_runway': '2',
            'arrival_metar': 'METAR data for arrival',
        }

        self.files = {
            'airframe_photo': SimpleUploadedFile("airframe.jpg", self.get_image_buffer().read()),
            'meal_photo': SimpleUploadedFile("meal.jpg", self.get_image_buffer().read()),
            'form-TOTAL_FORMS': '10',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-track_img': SimpleUploadedFile("track1.jpg", self.get_image_buffer().read()),
            'form-1-track_img': SimpleUploadedFile("track2.jpg", self.get_image_buffer().read())
        }
