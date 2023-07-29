import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aviablog.settings")
import django
django.setup()

from datetime import time
from django.test import TestCase
from django.urls import reverse
from users.forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

UserClass = get_user_model()


class TestRegisterView(TestCase):

    def test_get(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_post_ok(self):
        payload = {
            'username': 'vovan',
            'email': 'vovan@mail.ru',
            'password1': 'inabat2023',
            'password2': 'inabat2023'
        }

        response = self.client.post(reverse('register'), data=payload)
        test_user = UserClass.objects.get(email='vovan@mail.ru')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(test_user.email, 'vovan@mail.ru')
        self.assertTrue(test_user.is_authenticated)

    def test_post_errors(self):
        payload = {
            'username': 'vovan',
            'email': 'vovan@mail.ru',
            'password1': '111',
        }

        response = self.client.post(reverse('register'), data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        self.assertIn('password2', response.context['form'].errors)