from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class AircraftType(models.Model):
    manufacturer = models.CharField(
        max_length=50,
        verbose_name='Производитель'
    )
    generic_type = models.CharField(
        max_length=50,
        verbose_name='Тип ВС'
    )

    class Meta:
        verbose_name = 'Тип самолета'
        verbose_name_plural = 'Типы самолетов'
        unique_together = ('manufacturer', 'generic_type')

    def __str__(self):
        return f'{self.manufacturer} {self.generic_type}'


class Airline(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название авиакомпании'
    )

    class Meta:
        verbose_name = 'Авиакомпания'
        verbose_name_plural = 'Авиакомпании'

    def __str__(self):
        return self.name


class Airframe(models.Model):
    serial_number = models.CharField(
        max_length=50,
        verbose_name='Серийный номер'
    )
    registration_number = models.CharField(
        max_length=50,
        verbose_name='Регистрационный номер'
    )

    def get_airframe_image_path(self, filename):
        *old_name, format = filename.split('.')
        new_filename = '.'.join((self.registration_number, format))
        return f'airframes/{self.airline.name}/{new_filename}'.lower()

    photo = models.ImageField(
        upload_to=get_airframe_image_path,
        verbose_name='Фото ВС'
    )
    aircraft_type = models.ForeignKey(
        to='AircraftType',
        on_delete=models.SET_NULL,
        null=True,
        related_name='airframes',
        verbose_name='Тип ВС'
    )
    airline = models.ForeignKey(
        to='Airline',
        on_delete=models.SET_NULL,
        null=True,
        related_name='fleet',
        verbose_name='Авиакомпания'
    )

    class Meta:
        verbose_name = 'Воздушное судно'
        verbose_name_plural = 'Воздушные судна'
        unique_together = ('serial_number', 'registration_number')

    def __str__(self):
        return f'Борт {self.registration_number}'


class FlightInfo(models.Model):
    DEPARTURE = 'Departure'
    ARRIVAL = 'Arrival'
    STATUS_CHOICES = [
        (DEPARTURE, 'Departure'),
        (ARRIVAL, 'Arrival'),
    ]

    flight = models.ForeignKey(
        to='Flight',
        on_delete=models.CASCADE,
        verbose_name='Полет'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Вылет/Прилет'
    )
    airport_code = models.CharField(
        max_length=4,
        verbose_name='IATA-код аэропорта'
    )
    metar = models.CharField(
        max_length=300,
        verbose_name='METAR',
        blank=True,
        null=True
    )
    gate = models.CharField(
        max_length=5,
        verbose_name='Гейт',
        blank=True,
        null=True
    )
    is_boarding_bridge = models.BooleanField(
        verbose_name='Через телетрап',
        default=False
    )
    schedule_time = models.TimeField(
        verbose_name='Время рассчетное',
        blank=True,
        null=True
    )
    actual_time = models.TimeField(
        verbose_name='Время фактическое',
        blank=True,
        null=True
    )
    runway = models.CharField(
        max_length=3,
        verbose_name='Активная ВПП'
    )

    class Meta:
        verbose_name = 'Дополнительная информация о полете'
        verbose_name_plural = 'Дополнительная информация о полете'
        unique_together = ('flight', 'airport_code')

    def __str__(self):
        tail = self.status + ': ' + self.airport_code
        return f'{self.flight.__str__()}/{tail}'


class Flight(models.Model):
    flight_number = models.CharField(
        max_length=50,
        verbose_name='Номер рейса'
    )
    airframe = models.ForeignKey(
        to='Airframe',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Воздушное судно'
    )

    date = models.DateField(
        verbose_name='Дата полета',
    )

    flight_time = models.TimeField(
        verbose_name='Время полета',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Совершенный полет'
        verbose_name_plural = 'Совершенные полеты'
        unique_together = ('flight_number', 'date')

    def __str__(self):
        return f'Совершенный полет {self.flight_number}/{self.date}'

    def delete(self, using=None, keep_parents=False):
        airframe = self.airframe
        other_flight_count = Flight.objects.filter(airframe=airframe).exclude(pk=self.pk).count()
        if other_flight_count == 0:
            airframe.delete(using=using, keep_parents=keep_parents)
        super(Flight, self).delete(using=using, keep_parents=keep_parents)


class UserTrip(models.Model):
    flight = models.ForeignKey(
        to='Flight',
        on_delete=models.CASCADE,
        verbose_name='Полет'
    )
    passenger = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пассажир'
    )
    seat = models.CharField(
        max_length=4,
        verbose_name='Место',
        blank=True,
        null=True
    )
    neighbors = models.TextField(
        verbose_name='Соседи в полете',
        blank=True,
        null=True
    )
    comments = models.TextField(
        verbose_name='Комментарии',
        blank=True,
        null=True
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена билета',
        blank=True,
        null=True
    )
    slug = models.SlugField(
        blank=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Путешествие пользователя'
        verbose_name_plural = 'Путешествия пользователей'
        unique_together = ('flight', 'passenger')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.flight.flight_number}-{self.flight.date}-{self.passenger.username}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Путешествие {self.flight.flight_number}-{self.flight.date}-{self.passenger.username}"

    def delete(self, using=None, keep_parents=False):
        flight = self.flight
        other_usertrip_count = UserTrip.objects.filter(flight=flight).exclude(pk=self.pk).count()
        if other_usertrip_count == 0:
            flight.delete(using=using, keep_parents=keep_parents)
        super(UserTrip, self).delete(using=using, keep_parents=keep_parents)


class TrackImage(models.Model):
    trip = models.ForeignKey(
        to='UserTrip',
        on_delete=models.CASCADE,
        verbose_name='Полет пользователя'
    )

    def get_airframe_image_path(self, filename):
        return f'tracks/{self.trip.passenger.username}/' \
               f'{self.trip.flight.flight_number}/' \
               f'{self.trip.flight.date}/' \
               f'{filename}'.lower()

    track_img = models.ImageField(
        upload_to=get_airframe_image_path,
        verbose_name='Изображение трэка',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Изображения трэка'
        verbose_name_plural = 'Изображения трэков'

    def __str__(self):
        return f'Трэк {str(self.track_img.url)}'


class Meal(models.Model):
    trip = models.ForeignKey(
        to='UserTrip',
        on_delete=models.CASCADE,
        verbose_name='Путешествие',
        default=1
    )
    drinks = models.TextField(verbose_name='Предложенные напитки', default='Вода')
    appertize = models.TextField(verbose_name='Предложенные закуски', default='')
    main_course = models.TextField(verbose_name='Основные блюда', default='')
    desert = models.TextField(verbose_name='Предложенные десерты', default='')
    meal_price = models.PositiveSmallIntegerField(
        verbose_name='Цена питания',
        blank=True,
        null=True
    )

    def get_airframe_image_path(self, filename):
        return f'meal/{self.trip.flight.flight_number}/' \
               f'{self.trip.flight.date}/' \
               f'{filename}'.lower()

    meal_photo = models.ImageField(
        upload_to=get_airframe_image_path,
        verbose_name='Фотография питания',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Питание в полете'
        verbose_name_plural = 'Питание в полете'

    def __str__(self):
        return f'Питание на рейсе {self.trip.flight.flight_number}/{self.trip.flight.date}'
