import shutil
import tempfile
from aviablog import settings
from django.test import TestCase, override_settings
from django.core.management import call_command

from flights.factories import UserTripFactory, FlightInfoFactory, MealFactory, TrackImageFactory

tmp_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=tmp_dir)
class UploadDataMixin(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tmp_dir

        # Вызываем команду flush для очистки базы данных
        call_command('flush', interactive=False)

    def setUp(self):
        super().setUp()

        # upload data to db
        usertrip_lst = UserTripFactory.create_batch(7)

        for usertrip in usertrip_lst:
            FlightInfoFactory(flight=usertrip.flight)
            FlightInfoFactory(flight=usertrip.flight)
            MealFactory(trip=usertrip)
            TrackImageFactory(trip=usertrip)


    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(cls.media_root)
