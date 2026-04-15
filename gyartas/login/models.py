from django.db import models

class Felhasznalo(models.Model):
    felhasznalo_id = models.CharField(max_length=16, primary_key=True)
    teljes_nev = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    felhasznalonev = models.CharField(max_length=50)
    jelszo = models.CharField(max_length=255)
    vonalkod = models.CharField(max_length=100, unique=True, null=True, blank=True)
    szerepkor = models.CharField(max_length=20, choices=[
        ('operator', 'Operátor'),
        ('vezeto', 'Vezető'),
        ('admin', 'Admin')
    ], default='operator')

    def __str__(self):
        return self.teljes_nev
