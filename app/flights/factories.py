from factory import Factory, Faker

from flights.models import AircraftType


class AircraftTypeFactory(Factory):
    class Meta:
        model = AircraftType

    manufacturer = Faker('company')
    generic_type = Faker('random_int', min=100, max=999)