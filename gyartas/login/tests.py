from django.test import TestCase

from django.test import TestCase
from django.urls import reverse

class LoginTest(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)


class LoginTest(TestCase):
    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'felhasznalonev': 'admin',
            'jelszo': 'rosszjelszo'
        })
        self.assertContains(response, "Hibás felhasználónév vagy jelszó")


from login.models import Felhasznalo

class LoginTest(TestCase):
    def test_login_success_redirect(self):
        Felhasznalo.objects.create(
            felhasznalonev='teszt',
            jelszo='teszt',
            szerepkor='operator'
        )
        response = self.client.post(reverse('login'), {
            'felhasznalonev': 'teszt',
            'jelszo': 'teszt'
        })
        self.assertEqual(response.status_code, 302)
