from django.db import models
from login.models import Felhasznalo


class Cikk(models.Model):
    cikkszam = models.CharField(max_length=20, primary_key=True)
    tipus = models.CharField(max_length=20, choices=[
        ('alapanyag', 'Alapanyag'),
        ('kesztermek', 'Késztermék')
    ])
    megnevezes = models.CharField(max_length=100)
    minoseg = models.CharField(max_length=50, null=True, blank=True)
    magassag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    szelesseg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hosszusag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"{self.cikkszam} - {self.megnevezes}"



class Muvelet(models.Model):
    muvelet_id = models.AutoField(primary_key=True)
    megnevezes = models.CharField(max_length=100)
    koltseg = models.DecimalField(max_digits=10, decimal_places=2)
    normaido = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.megnevezes


class Partner(models.Model):
    partner_id = models.AutoField(primary_key=True)
    partner_nev = models.CharField(max_length=255)
    adoszam = models.CharField(max_length=20, blank=True, null=True)
    cim = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefonszam = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.partner_nev



class ReceptFej(models.Model):
    recept_id = models.AutoField(primary_key=True)
    kesztermek_cikkszam = models.ForeignKey(Cikk, on_delete=models.CASCADE)
    anyaghanyad = models.DecimalField(max_digits=10, decimal_places=2)
    letrehozas_datuma = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recept #{self.recept_id}"


class ReceptSor(models.Model):
    sor_id = models.AutoField(primary_key=True)
    recept = models.ForeignKey(ReceptFej, on_delete=models.CASCADE)
    alapanyag_cikkszam = models.ForeignKey(Cikk, on_delete=models.CASCADE)
    mennyiseg = models.DecimalField(max_digits=10, decimal_places=2)
    muvelet = models.ForeignKey(Muvelet, on_delete=models.CASCADE, null=True, blank=True)
    sorrend = models.IntegerField(default=1)


    def __str__(self):
        return f"Sor #{self.sor_id}"


class GyartasFej(models.Model):
    gyartas_id = models.AutoField(primary_key=True)
    kesztermek_cikkszam = models.ForeignKey(Cikk, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    tervezett_mennyiseg = models.IntegerField()
    jo_mennyiseg = models.IntegerField(default=0)
    selejt_mennyiseg = models.IntegerField(default=0)
    statusz = models.CharField(max_length=20, choices=[
        ('tervezett', 'Tervezett'),
        ('engedelyezett', 'Engedélyezett'),
        ('lezart', 'Lezárt')
    ], default='tervezett')
    letrehozas_datuma = models.DateTimeField(auto_now_add=True)
    lezaras_datuma = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Gyártás #{self.gyartas_id}"


class GyartasSor(models.Model):
    gyartas_sor_id = models.AutoField(primary_key=True)
    gyartas = models.ForeignKey(GyartasFej, on_delete=models.CASCADE)
    muvelet = models.ForeignKey(Muvelet, on_delete=models.CASCADE)
    sorrend = models.IntegerField()
    tervezett_db = models.IntegerField()
    jo_db = models.IntegerField(default=0)
    selejt_db = models.IntegerField(default=0)

    def __str__(self):
        return f"Gyártás sor #{self.gyartas_sor_id}"


class Lejelentes(models.Model):
    lejelentes_id = models.AutoField(primary_key=True)

    # MŰVELET SZINTŰ lejelentéshez (régi rendszer)
    gyartas_sor = models.ForeignKey(GyartasSor, null=True, blank=True, on_delete=models.CASCADE)

    # ÚJ: GYÁRTÁS SZINTŰ lejelentéshez
    gyartas = models.ForeignKey(GyartasFej, null=True, blank=True, on_delete=models.CASCADE)

    felhasznalo = models.ForeignKey(Felhasznalo, on_delete=models.CASCADE)
    bemeno_db = models.IntegerField()
    jo_db = models.IntegerField()
    selejt_db = models.IntegerField()
    datum = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lejelentés #{self.lejelentes_id}"




#------------------------

class Keszlet(models.Model):
    cikk = models.OneToOneField(Cikk, on_delete=models.CASCADE, primary_key=True)
    mennyiseg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.cikk.megnevezes} – {self.mennyiseg} db"




class KeszletMozgas(models.Model):
    cikk = models.ForeignKey(Cikk, on_delete=models.CASCADE)
    mennyiseg = models.DecimalField(max_digits=10, decimal_places=2)
    tipus = models.CharField(max_length=20, choices=[
        ('felhasznalas', 'Felhasználás'),
        ('gyartas', 'Gyártás'),
        ('korrekcio', 'Korrekció')
    ])
    datum = models.DateTimeField(auto_now_add=True)
    gyartas = models.ForeignKey(GyartasFej, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.cikk.megnevezes} – {self.tipus} – {self.mennyiseg}"



