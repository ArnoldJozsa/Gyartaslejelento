from django.test import TestCase
from gyartas_app.models import GyartasFej, Partner, Cikk
from gyartas_app.models import Lejelentes
from login.models import Felhasznalo

class GyartasTest(TestCase):
    def test_create_gyartas(self):
        partner = Partner.objects.create(partner_nev="Teszt Kft", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")

        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=10,
            statusz="tervezett"
        )

        self.assertEqual(gy.tervezett_mennyiseg, 10)


class GyartasTest(TestCase):
    def test_status_change(self):
        partner = Partner.objects.create(partner_nev="Teszt", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")

        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=5,
            statusz="tervezett"
        )

        gy.statusz = "engedelyezett"
        gy.save()

        self.assertEqual(gy.statusz, "engedelyezett")


class GyartasTest(TestCase):
    def test_lezaras_jo_mennyiseg(self):
        partner = Partner.objects.create(partner_nev="Teszt", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")

        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=10,
            jo_mennyiseg=7,
            selejt_mennyiseg=3,
            statusz="engedelyezett"
        )

        self.assertEqual(gy.jo_mennyiseg, 7)



class LejelentesTest(TestCase):
    def test_create_lejelentes(self):
        user = Felhasznalo.objects.create(
            felhasznalonev="op",
            jelszo="123",
            szerepkor="operator"
        )
        partner = Partner.objects.create(partner_nev="Teszt", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")
        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=10
        )

        le = Lejelentes.objects.create(
            gyartas=gy,
            felhasznalo=user,
            bemeno_db=10,
            jo_db=8,
            selejt_db=2
        )

        self.assertEqual(le.jo_db, 8)


class LejelentesTest(TestCase):
    def test_selejt_szamolas(self):
        user = Felhasznalo.objects.create(
            felhasznalonev="op",
            jelszo="123",
            szerepkor="operator"
        )
        partner = Partner.objects.create(partner_nev="Teszt", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")
        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=10
        )

        le = Lejelentes.objects.create(
            gyartas=gy,
            felhasznalo=user,
            bemeno_db=10,
            jo_db=9,
            selejt_db=1
        )

        self.assertEqual(le.selejt_db, 1)

class LejelentesTest(TestCase):
    def test_lejelentes_date(self):
        user = Felhasznalo.objects.create(
            felhasznalonev="op",
            jelszo="123",
            szerepkor="operator"
        )
        partner = Partner.objects.create(partner_nev="Teszt", adoszam="123")
        cikk = Cikk.objects.create(cikkszam="A1", megnevezes="Termék", tipus="kesztermek")
        gy = GyartasFej.objects.create(
            kesztermek_cikkszam=cikk,
            partner=partner,
            tervezett_mennyiseg=10
        )

        le = Lejelentes.objects.create(
            gyartas=gy,
            felhasznalo=user,
            bemeno_db=10,
            jo_db=10,
            selejt_db=0
        )

        self.assertIsNotNone(le.datum)
