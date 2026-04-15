from django.test import TestCase
from django.urls import reverse

class AdminTest(TestCase):
    def test_admin_cikkek_page(self):
        response = self.client.get(reverse('admin_cikkek'))
        self.assertEqual(response.status_code, 200)

class AdminTest(TestCase):
    def test_admin_create_cikk(self):
        response = self.client.post(reverse('admin_cikk_uj'), {
            'cikkszam': 'T100',
            'megnevezes': 'Teszt cikk',
            'tipus': 'alapanyag'
        })
        self.assertEqual(response.status_code, 302)


class AdminTest(TestCase):
    def test_admin_partner_page(self):
        response = self.client.get(reverse('admin_partnerek'))
        self.assertEqual(response.status_code, 200)
