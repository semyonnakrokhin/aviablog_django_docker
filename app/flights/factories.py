import string
import random

import factory
from django.utils.text import slugify

from users.factories import UserFactory
from .models import (Flight,
                     Airline,
                     AircraftType,
                     Airframe,
                     UserTrip,
                     Meal,
                     FlightInfo,
                     TrackImage)


class AircraftTypeFactory(factory.django.DjangoModelFactory):
    '''unique_together = ('manufacturer', 'generic_type')'''

    manufacturer = factory.Sequence(lambda n: f'Manufacturer{n}')
    generic_type = factory.Sequence(lambda n: f'Generic Type{n}')

    class Meta:
        model = AircraftType


class AirlineFactory(factory.django.DjangoModelFactory):
    '''unique name'''

    name = factory.Sequence(lambda n: f'Airline{n}')

    class Meta:
        model = Airline


class AirframeFactory(factory.django.DjangoModelFactory):
    '''unique_together = ('serial_number', 'registration_number')'''

    serial_number = factory.Sequence(lambda n: f'SN{n:04}')
    registration_number = factory.Sequence(lambda n: f'RA-{n:05}')
    photo = factory.django.ImageField()
    aircraft_type = factory.SubFactory(AircraftTypeFactory)
    airline = factory.SubFactory(AirlineFactory)

    class Meta:
        model = Airframe


class FlightFactory(factory.django.DjangoModelFactory):
    '''('flight_number', 'date')'''

    flight_number = factory.Faker('bothify', text='??#??#?#')
    airframe = factory.SubFactory(AirframeFactory)
    date = factory.Faker('date_between', start_date='-30d', end_date='+30d')
    flight_time = factory.Faker('time_object')

    class Meta:
        model = Flight


class UserTripFactory(factory.django.DjangoModelFactory):
    '''unique_together = ('flight', 'passenger')'''

    flight = factory.SubFactory(FlightFactory)
    passenger = factory.SubFactory(UserFactory)
    seat = factory.Faker('bothify', text='??#')
    neighbors = factory.Faker('paragraph', nb_sentences=3)
    comments = factory.Faker('paragraph', nb_sentences=5)
    price = factory.Faker('pyint', min_value=1000, max_value=5000)

    class Meta:
        model = UserTrip

    @factory.lazy_attribute
    def slug(self):
        return slugify(f"{self.flight.flight_number}-{self.flight.date}-{self.passenger.username}")


def random_iata(*args, **kwargs):
    return ''.join(random.choices(string.ascii_uppercase, k=3))

def random_runway(*args, **kwargs):
    return f'{random.randint(1, 36):02}'


class FlightInfoFactory(factory.django.DjangoModelFactory):
    '''unique_together = ('flight', 'airport_code')'''

    flight = factory.SubFactory(FlightFactory)
    status = factory.Iterator([FlightInfo.DEPARTURE, FlightInfo.ARRIVAL])
    airport_code = factory.LazyFunction(random_iata)
    metar = factory.Faker('text')
    gate = factory.Sequence(lambda n: f'{n}')
    is_boarding_bridge = factory.Faker('boolean')
    schedule_time = factory.Faker('time_object')
    actual_time = factory.Faker('time_object')
    runway = factory.Sequence(random_runway)

    class Meta:
        model = FlightInfo


class TrackImageFactory(factory.django.DjangoModelFactory):
    trip = factory.SubFactory(UserTripFactory)
    track_img = factory.django.ImageField()
    class Meta:
        model = TrackImage


class MealFactory(factory.django.DjangoModelFactory):

    trip = factory.SubFactory(UserTripFactory)
    drinks = factory.Faker('text')
    appertize = factory.Faker('text')
    main_course = factory.Faker('text')
    desert = factory.Faker('text')
    meal_price = factory.Faker('pyint')
    meal_photo = factory.django.ImageField()
    class Meta:
        model = Meal
