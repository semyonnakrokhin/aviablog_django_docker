import factory
from django.contrib.auth import get_user_model

UserClass = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):

    username = factory.Sequence(lambda n: f'test_user_{n}')
    email = factory.Sequence(lambda n: f'test_user_{n}@mail.ru')
    password = factory.Faker('password')

    class Meta:
        model = UserClass