from django.contrib.auth.models import User
from django.db.models import Count, F, Prefetch
from django.db.models.functions import Concat

from .models import UserTrip, Flight, FlightInfo


class FlightInformationService:
    '''Бизнес-логика, отвечающая за получение общей информации о полетах из базы данных.
    Этот сервис может иметь методы для получения общего количества полетов,
    списка всех авиакомпаний, списка всех аэропортов и т.д.'''

    @staticmethod
    def get_latest_cards(max_count=6):
        latest_cards = UserTrip.objects \
                           .select_related('passenger', 'flight__airframe__aircraft_type', 'flight__airframe__airline') \
                           .prefetch_related('flight__flightinfo_set') \
                           .order_by('-id')[:max_count]

        cards = []

        try:
            for trip in latest_cards:
                card = {
                    'photo_url': trip.flight.airframe.photo,
                    'flight_number': trip.flight.flight_number,
                    'date': trip.flight.date,
                    'passenger': trip.passenger.username,
                    'airline': trip.flight.airframe.airline.name,
                    'aircraft_type': ' '.join((trip.flight.airframe.aircraft_type.manufacturer,
                                               trip.flight.airframe.aircraft_type.generic_type)),
                    'departure': trip.flight.flightinfo_set.get(status='Departure').airport_code,
                    'destination': trip.flight.flightinfo_set.get(status='Arrival').airport_code,
                    'usertripslug': trip.slug
                }
                cards.append(card)
        except:
            pass

        return cards

    @staticmethod
    def get_top_users(top=5):
        return UserTrip.objects \
                   .select_related('passenger') \
                   .values(username=F('passenger__username')) \
                   .annotate(total_flights=Count('flight')) \
                   .order_by('-total_flights')[:top]

    @staticmethod
    def get_site_information():
        queryset = FlightInfo.objects \
            .select_related('flight__airframe__aircraft_type', 'flight__airframe__airline') \
            .aggregate(unique_airlines=Count('flight__airframe__airline__name', distinct=True),
                       unique_aircraft_types=Count('flight__airframe__aircraft_type__pk', distinct=True),
                       unique_airframes=Count('flight__airframe__serial_number', distinct=True),
                       unique_airports=Count('airport_code', distinct=True))

        res = [{'title': k.replace('_', ' ').capitalize(), 'value': v} for k, v in queryset.items()]

        return res


class PassengerService:
    @staticmethod
    def get_all_passengers_with_statistic():
        '''Что входит: количество уникальных полетов, уникальных авиакомпаний, уникальных типов ВС, уникальных АП'''

        passengers_data = User.objects \
            .values('username', 'first_name', 'last_name') \
            .annotate(
            total_airlines=Count('usertrip__flight__airframe__airline', distinct=True),
            total_aircraft_types=Count('usertrip__flight__airframe__aircraft_type', distinct=True),
            total_airports=Count('usertrip__flight__flightinfo__airport_code', distinct=True),
            total_flights=Count('usertrip', distinct=True)
        ).order_by('username')

        return passengers_data


class PassengerProfileService:
    @staticmethod
    def get_profile_information(username):
        return PassengerService.get_all_passengers_with_statistic().get(username=username)

    @staticmethod
    def get_passenger_flights(username):
        object_or_set = UserTrip.objects \
            .select_related('flight__airframe__airline', 'passenger') \
            .prefetch_related('flight__flightinfo_set') \
            .filter(passenger__username=username) \
            .order_by('-flight__date')

        return object_or_set


class FlightDetailService:
    @staticmethod
    def get_flight_details(usertripslug):
        trip = UserTrip.objects \
            .select_related('passenger',
                            'flight__airframe__aircraft_type',
                            'flight__airframe__airline',
                            ) \
            .prefetch_related('flight__flightinfo_set',
                              'trackimage_set',
                              'meal_set') \
            .get(slug=usertripslug)

        flight = trip.flight
        meal = trip.meal_set.first()
        departure_info = flight.flightinfo_set.get(status='Departure')
        arrival_info = flight.flightinfo_set.get(status='Arrival')

        id_dict = {
            'usertrip_id': trip.id,
            'flight_id': flight.id,
            'meal_id': meal.id,
            'departure_id': departure_info.id,
            'arrival_id': arrival_info.id,
            'airframe_id': trip.flight.airframe.id,
            'aircraft_type_id': trip.flight.airframe.aircraft_type.id,
            'airline_id': trip.flight.airframe.airline.id,
            **{f'track_image_{i}': track.id for i, track in enumerate(trip.trackimage_set.all())}
        }

        flight_dict = {
            'usertripslug': trip.slug,

            'registration_number': flight.airframe.registration_number,
            'serial_number': flight.airframe.serial_number,
            'airline_name': flight.airframe.airline.name,

            'flight_number': flight.flight_number,
            'date': flight.date.strftime('%Y-%m-%d'),
            'flight_time': flight.flight_time,

            'manufacturer': flight.airframe.aircraft_type.manufacturer,
            'generic_type': flight.airframe.aircraft_type.generic_type,
            'aircraft_type': ' '.join((flight.airframe.aircraft_type.manufacturer,
                                       flight.airframe.aircraft_type.generic_type)),

            'user': trip.passenger,
            'seat': trip.seat,
            'neighbors': trip.neighbors,
            'comments': trip.comments,
            'ticket_price': trip.price,

            'drinks': meal.drinks,
            'appertize': meal.appertize,
            'main_course': meal.main_course,
            'desert': meal.desert,
            'meal_price': meal.meal_price,

            'route': ' — '.join((departure_info.airport_code, arrival_info.airport_code)),

            'departure_info': departure_info,
            'arrival_info': arrival_info,

            'departure_airport_code': departure_info.airport_code ,
            'departure_gate': departure_info.gate,
            'departure_is_boarding_bridge': departure_info.is_boarding_bridge,
            'departure_schedule_time': departure_info.schedule_time,
            'departure_actual_time': departure_info.actual_time,
            'departure_runway': departure_info.runway,
            'departure_metar': departure_info.metar,

            'arrival_airport_code': arrival_info.airport_code ,
            'arrival_gate': arrival_info.gate,
            'arrival_is_boarding_bridge': arrival_info.is_boarding_bridge,
            'arrival_schedule_time': arrival_info.schedule_time,
            'arrival_actual_time': arrival_info.actual_time,
            'arrival_runway': arrival_info.runway,
            'arrival_metar': arrival_info.metar,

            'track_images': trip.trackimage_set.all(),
        }

        files = {
            'airframe_photo': flight.airframe.photo,
            'meal_photo': meal.meal_photo,
            **{f'track_image_{i}': track.track_img for i, track in enumerate(trip.trackimage_set.all())}
        }

        return flight_dict, files, id_dict
