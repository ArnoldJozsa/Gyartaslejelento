from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, 'gyartas_app/index.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import GyartasFej, ReceptSor, Keszlet, KeszletMozgas

def gyartas_lezaras(request, gyartas_id):
    gy = GyartasFej.objects.get(pk=gyartas_id)

    recept_sorok = ReceptSor.objects.filter(recept=gy.kesztermek_cikkszam.receptfej)

    hianyok = []
    for sor in recept_sorok:
        kell = sor.mennyiseg * gy.jo_mennyiseg
        keszlet = Keszlet.objects.get(cikk=sor.alapanyag_cikkszam)

        if keszlet.mennyiseg < kell:
            hianyok.append(f"{sor.alapanyag_cikkszam.megnevezes} – hiányzik {kell - keszlet.mennyiseg} db")

    if hianyok:
        messages.error(request, "Nincs elég alapanyag:")
        for h in hianyok:
            messages.error(request, h)
        return redirect('gyartas_reszletek', gyartas_id=gy.id)

    for sor in recept_sorok:
        kell = sor.mennyiseg * gy.jo_mennyiseg
        KeszletMozgas.objects.create(
            cikk=sor.alapanyag_cikkszam,
            mennyiseg=kell,
            tipus='felhasznalas',
            gyartas=gy
        )

    KeszletMozgas.objects.create(
        cikk=gy.kesztermek_cikkszam,
        mennyiseg=gy.jo_mennyiseg,
        tipus='gyartas',
        gyartas=gy
    )

    gy.statusz = 'lezart'
    gy.save()

    messages.success(request, "Gyártás sikeresen lezárva, készlet frissítve.")
    return redirect('gyartas_lista')
