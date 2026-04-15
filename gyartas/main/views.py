from tracemalloc import start

from django.shortcuts import render, redirect
from django.http import HttpResponse
from login.decorators import role_required
from login.models import Felhasznalo
from gyartas_app.models import (
    GyartasFej, GyartasSor, Lejelentes,
    Cikk, Muvelet, ReceptFej, ReceptSor,
    Partner,Keszlet, KeszletMozgas
)
import datetime
import io
import xlsxwriter
from datetime import date
from django.db.models import Sum
from decimal import Decimal






def main_view(request):
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    return render(request, 'main/main.html')


def login_redirect(request):
    return redirect('login')




@role_required(['operator', 'vezeto', 'admin'])
def operator_riport(request):
    from datetime import datetime, date, time
    from django.utils.timezone import make_aware

    
    datum_str = request.GET.get("datum")

    if datum_str:
        try:
            
            datum = datetime.strptime(datum_str, "%Y-%m-%d").date()
        except:
            datum = date.today()
    else:
        datum = date.today()

    start = make_aware(datetime.combine(datum, time.min))
    end = make_aware(datetime.combine(datum, time.max))

    
    sorok = Lejelentes.objects.filter(datum__range=(start, end)).order_by("datum")

    
    return render(request, 'main/operator_riport.html', {
        'sorok': sorok,
        'datum': datum  
    })




@role_required(['operator','vezeto', 'admin'])
def operator_riport_export(request):

    datum_str = request.GET.get("datum")

    if datum_str:
        try:
            datum = datetime.datetime.strptime(datum_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                datum = datetime.datetime.strptime(datum_str, "%B %d, %Y").date()
            except ValueError:
                datum = datetime.date.today()
    else:
        datum = datetime.date.today()

    from datetime import time
    from django.utils.timezone import make_aware

    start = make_aware(datetime.datetime.combine(datum, time.min))
    end = make_aware(datetime.datetime.combine(datum, time.max))

    sorok = Lejelentes.objects.filter(datum__range=(start, end))



    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Napi riport")

    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })

    cell_format = workbook.add_format({'border': 1})

    headers = ["Gyártás ID", "Művelet", "Felhasználó", "Jó db", "Selejt db", "Dátum", "Partner"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    for row, s in enumerate(sorok, start=1):

        
        if s.gyartas_sor:
            worksheet.write(row, 0, s.gyartas_sor.gyartas.gyartas_id, cell_format)
        else:
            worksheet.write(row, 0, s.gyartas.gyartas_id, cell_format)

        
        if s.gyartas_sor:
            worksheet.write(row, 1, s.gyartas_sor.muvelet.megnevezes, cell_format)
        else:
            worksheet.write(row, 1, "Teljes gyártás", cell_format)

        worksheet.write(row, 2, s.felhasznalo.felhasznalonev, cell_format)
        worksheet.write(row, 3, s.jo_db, cell_format)
        worksheet.write(row, 4, s.selejt_db, cell_format)
        worksheet.write(row, 5, str(s.datum), cell_format)
        worksheet.write(row, 6, s.gyartas.partner.partner_nev, cell_format)

    workbook.close()

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=napi_riport_{datum}.xlsx'

    return response



@role_required(['operator','vezeto', 'admin'])
def operator_riport_pdf(request):
    import pdfkit
    from django.template.loader import render_to_string

    datum_str = request.GET.get("datum")

    if datum_str:
        try:
            datum = datetime.datetime.strptime(datum_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                datum = datetime.datetime.strptime(datum_str, "%B %d, %Y").date()
            except ValueError:
                datum = datetime.date.today()
    else:
        datum = datetime.date.today()
    from datetime import time
    from django.utils.timezone import make_aware
    
    start = make_aware(datetime.datetime.combine(datum, time.min))
    end = make_aware(datetime.datetime.combine(datum, time.max))

    sorok = Lejelentes.objects.filter(datum__range=(start, end))

    from django.utils.timezone import now
    html = render_to_string('main/operator_riport_pdf.html', {
        'sorok': sorok,
        'datum': datum,
        'generated_at': now()
    })

    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    pdf = pdfkit.from_string(html, False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=napi_riport_{datum}.pdf"'

    return response






@role_required(['operator', 'admin'])
def operator_gyartasok(request):
    
    gyartasok = GyartasFej.objects.exclude(statusz='tervezett').order_by('-gyartas_id')
    return render(request, 'main/operator_gyartasok.html', {'gyartasok': gyartasok})


@role_required(['operator', 'admin'])
def operator_gyartas_reszletek(request, id):
    gyartas = GyartasFej.objects.get(gyartas_id=id)
    sorok = GyartasSor.objects.filter(gyartas=gyartas).order_by('sorrend')

    
    kov_sor = sorok.filter(jo_db=0, selejt_db=0).order_by('sorrend').first()

    return render(request, 'main/operator_gyartas_reszletek.html', {
        'gyartas': gyartas,
        'kov_sor': kov_sor,
        'sorok': sorok
    })



@role_required(['operator', 'vezeto', 'admin'])
def operator_lejelentes(request, id):
    gyartas = GyartasFej.objects.get(gyartas_id=id)

    if request.method == 'POST':
        bemeno = int(request.POST.get('bemeno'))
        jo = int(request.POST.get('jo'))
        selejt = int(request.POST.get('selejt'))

        
        gyartas.jo_mennyiseg += jo
        gyartas.selejt_mennyiseg += selejt
        gyartas.save()

        
        felhasznalo = Felhasznalo.objects.get(
            felhasznalonev=request.session['felhasznalonev']
        )

        Lejelentes.objects.create(
            gyartas=gyartas,
            felhasznalo=felhasznalo,
            bemeno_db=bemeno,
            jo_db=jo,
            selejt_db=selejt
        )

        return redirect('operator_gyartas_reszletek', id=gyartas.gyartas_id)

    return render(request, 'main/operator_lejelentes.html', {
        'gyartas': gyartas
    })


@role_required(['vezeto', 'admin'])
def vezeto_dashboard(request):
    return render(request, 'main/vezeto_dashboard.html')

def nincs_jogosultsag(request):
    return render(request, 'main/nincs_jogosultsag.html')

@role_required(['vezeto', 'admin'])
def vezeto_gyartasok(request):
    gyartasok = GyartasFej.objects.all().order_by('-gyartas_id')

    for g in gyartasok:
        if g.statusz == "tervezett":
            g.statusz_display = "tervezett"
        elif g.statusz == "engedelyezett":
            g.statusz_display = "engedélyezett"
        elif g.statusz == "lezart":
            g.statusz_display = "lezárt"

    return render(request, 'main/vezeto_gyartasok.html', {
        'gyartasok': gyartasok
    })







@role_required(['vezeto', 'admin'])
def vezeto_gyartas_reszletek(request, id):
    gy = GyartasFej.objects.get(gyartas_id=id)
    sorok = GyartasSor.objects.filter(gyartas=gy).order_by('sorrend')

    return render(request, 'main/vezeto_gyartas_reszletek.html', {
        'gyartas': gy,
        'sorok': sorok
    })


from decimal import Decimal

@role_required(['vezeto', 'admin'])
def vezeto_gyartas_lezar(request, id):
    gy = GyartasFej.objects.get(gyartas_id=id)

    if gy.statusz == "lezart":
        gy.statusz = "engedelyezett"
        gy.save()


    osszes_jo = gy.jo_mennyiseg
    osszes_selejt = gy.selejt_mennyiseg


    gy.statusz = 'lezart'
    gy.lezaras_datuma = datetime.datetime.now()
    gy.save()


    recept = ReceptFej.objects.get(kesztermek_cikkszam=gy.kesztermek_cikkszam)
    recept_sorok = ReceptSor.objects.filter(recept=recept)


    for rs in recept_sorok:
        felhasznalt = rs.mennyiseg * osszes_jo
        keszlet = Keszlet.objects.get(cikk=rs.alapanyag_cikkszam)
        keszlet.mennyiseg -= felhasznalt
        keszlet.save()

        KeszletMozgas.objects.create(
            cikk=rs.alapanyag_cikkszam,
            mennyiseg=-felhasznalt,
            tipus='felhasznalas',
            gyartas=gy
        )

    
    kesztermek = gy.kesztermek_cikkszam
    keszlet_kesztermek, _ = Keszlet.objects.get_or_create(cikk=kesztermek)
    keszlet_kesztermek.mennyiseg += osszes_jo
    keszlet_kesztermek.save()

    KeszletMozgas.objects.create(
        cikk=kesztermek,
        mennyiseg=osszes_jo,
        tipus='gyartas',
        gyartas=gy
    )

    return redirect('vezeto_gyartasok')




@role_required(['vezeto', 'admin'])
def vezeto_gyartas_uj(request):
    if request.method == 'POST':
        kesztermek = request.POST.get('kesztermek')
        partner = request.POST.get('partner')
        mennyiseg = int(request.POST.get('mennyiseg'))

        
        try:
            recept = ReceptFej.objects.get(kesztermek_cikkszam=kesztermek)
        except ReceptFej.DoesNotExist:
            return render(request, 'main/vezeto_gyartas_uj.html', {
                'kesztermekek': Cikk.objects.filter(tipus='kesztermek'),
                'partnerek': Partner.objects.all(),
                'error': 'Ehhez a késztermékhez nincs recept létrehozva!'
            })

        
        gy = GyartasFej.objects.create(
            kesztermek_cikkszam_id=kesztermek,
            partner_id=partner,
            tervezett_mennyiseg=mennyiseg,
            statusz='tervezett'
        )

        
        sorok = ReceptSor.objects.filter(recept=recept).order_by('sorrend')

        for s in sorok:
            GyartasSor.objects.create(
                gyartas=gy,
                muvelet=s.muvelet,
                sorrend=s.sorrend,
                tervezett_db=mennyiseg,
                jo_db=0,
                selejt_db=0
            )

        return redirect('vezeto_gyartasok')

    
    kesztermekek = Cikk.objects.filter(tipus='kesztermek')
    partnerek = Partner.objects.all()

    return render(request, 'main/vezeto_gyartas_uj.html', {
        'kesztermekek': kesztermekek,
        'partnerek': partnerek
    })


@role_required(['vezeto', 'admin'])
def vezeto_gyartas_lejelentes(request, id):
    gy = GyartasFej.objects.get(gyartas_id=id)

    
    sorok = GyartasSor.objects.filter(gyartas=gy).order_by('sorrend')
    elso = sorok.first()

    bemeno = gy.tervezett_mennyiseg
    jo = elso.jo_db
    selejt = elso.selejt_db

    if request.method == 'POST':

        
        gy.jo_mennyiseg = jo
        gy.selejt_mennyiseg = selejt
        gy.save()

        
        Lejelentes.objects.create(
            gyartas=gy,
            felhasznalo=Felhasznalo.objects.get(
                felhasznalonev=request.session['felhasznalonev']
            ),
            bemeno_db=bemeno,
            jo_db=jo,
            selejt_db=selejt
        )

        return redirect('/vezeto/gyartas/' + str(id) + '/')

    return render(request, 'main/vezeto_lejelentes.html', {
        'gyartas': gy,
        'bemeno': bemeno,
        'osszes_jo': jo,
        'osszes_selejt': selejt
    })


@role_required(['admin'])
def admin_cikkek(request):
    cikkek = Cikk.objects.all()
    return render(request, 'main/admin_cikkek.html', {'cikkek': cikkek})


@role_required(['admin'])
def admin_cikk_uj(request):
    if request.method == 'POST':
        Cikk.objects.create(
            cikkszam=request.POST.get('cikkszam'),
            megnevezes=request.POST.get('megnevezes'),
            tipus=request.POST.get('tipus'),
            minoseg=request.POST.get('minoseg'),
            magassag=request.POST.get('magassag') or None,
            szelesseg=request.POST.get('szelesseg') or None,
            hosszusag=request.POST.get('hosszusag') or None
        )
        return redirect('admin_cikkek')

    return render(request, 'main/admin_cikk_uj.html')



@role_required(['admin'])
def admin_muveletek(request):
    muveletek = Muvelet.objects.all().order_by('muvelet_id')
    return render(request, 'main/admin_muveletek.html', {'muveletek': muveletek})


@role_required(['admin'])
def admin_muvelet_uj(request):
    if request.method == 'POST':
        Muvelet.objects.create(
            megnevezes=request.POST.get('megnevezes'),
            koltseg=request.POST.get('koltseg'),
            normaido=request.POST.get('normaido')
        )
        return redirect('admin_muveletek')

    return render(request, 'main/admin_muvelet_uj.html')


@role_required(['admin'])
def admin_muvelet_szerkeszt(request, id):
    muvelet = Muvelet.objects.get(muvelet_id=id)

    if request.method == 'POST':
        muvelet.megnevezes = request.POST.get('megnevezes')
        muvelet.koltseg = request.POST.get('koltseg')
        muvelet.normaido = request.POST.get('normaido')
        muvelet.save()
        return redirect('admin_muveletek')

    return render(request, 'main/admin_muvelet_szerkeszt.html', {'muvelet': muvelet})


@role_required(['admin'])
def admin_muvelet_torol(request, id):
    Muvelet.objects.get(muvelet_id=id).delete()
    return redirect('admin_muveletek')


@role_required(['admin'])
def admin_recept_lista(request):
    receptek = ReceptFej.objects.all().order_by('-recept_id')
    return render(request, 'main/admin_recept_lista.html', {'receptek': receptek})


@role_required(['admin'])
def admin_recept_uj(request):
    if request.method == 'POST':
        recept = ReceptFej.objects.create(
            kesztermek_cikkszam_id=request.POST.get('kesztermek'),
            anyaghanyad=request.POST.get('anyaghanyad')
        )
        return redirect('admin_recept_sorok', id=recept.recept_id)

    kesztermekek = Cikk.objects.filter(tipus='kesztermek')
    return render(request, 'main/admin_recept_uj.html', {'kesztermekek': kesztermekek})


@role_required(['admin'])
def admin_recept_sorok(request, id):
    recept = ReceptFej.objects.get(recept_id=id)
    sorok = ReceptSor.objects.filter(recept=recept).order_by('sorrend')

    if request.method == 'POST':
        ReceptSor.objects.create(
            recept=recept,
            alapanyag_cikkszam_id=request.POST.get('alapanyag'),
            mennyiseg=request.POST.get('mennyiseg'),
            muvelet_id=request.POST.get('muvelet'),
            sorrend=request.POST.get('sorrend')
        )
        return redirect('admin_recept_sorok', id=id)

    return render(request, 'main/admin_recept_sorok.html', {
        'recept': recept,
        'sorok': sorok,
        'alapanyagok': Cikk.objects.filter(tipus='alapanyag'),
        'muveletek': Muvelet.objects.all()
    })

@role_required(['admin'])
def admin_partnerek(request):
    partnerek = Partner.objects.all().order_by('partner_nev')
    return render(request, 'main/admin_partnerek.html', {'partnerek': partnerek})


@role_required(['admin'])
def admin_partner_uj(request):
    if request.method == 'POST':
        Partner.objects.create(
            partner_nev=request.POST.get('partner_nev'),
            adoszam=request.POST.get('adoszam'),
            cim=request.POST.get('cim'),
            email=request.POST.get('email'),
            telefonszam=request.POST.get('telefonszam')
        )
        return redirect('admin_partnerek')

    return render(request, 'main/admin_partner_uj.html')


@role_required(['admin'])
def admin_partner_szerkeszt(request, id):
    partner = Partner.objects.get(partner_id=id)

    if request.method == 'POST':
        partner.partner_nev = request.POST.get('partner_nev')
        partner.adoszam = request.POST.get('adoszam')
        partner.cim = request.POST.get('cim')
        partner.email = request.POST.get('email')
        partner.telefonszam = request.POST.get('telefonszam')
        partner.save()
        return redirect('admin_partnerek')

    return render(request, 'main/admin_partner_szerkeszt.html', {'partner': partner})


@role_required(['admin'])
def admin_partner_torol(request, id):
    Partner.objects.get(partner_id=id).delete()
    return redirect('admin_partnerek')

@role_required(['admin'])
def admin_recept_torol(request, id):
    ReceptFej.objects.get(recept_id=id).delete()
    return redirect('admin_recept_lista')




import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse

def nav_lekerdezes(request, adoszam):
    if not adoszam:
        return JsonResponse({"error": "Nincs adószám megadva"}, status=400)

    
    url = f"https://nav.gov.hu/adatbazisok/adotorzs?query={adoszam}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except:
        return JsonResponse({"error": "NAV oldal nem elérhető"}, status=503)

    soup = BeautifulSoup(r.text, "html.parser")

    cegnev = None
    cim = None

    
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)

            if label == "Név":
                cegnev = value
            if label == "Cím":
                cim = value

    
    if not cegnev:
        return JsonResponse({"error": "Nem található adat az adószámhoz"}, status=404)

    return JsonResponse({
        "cegnev": cegnev,
        "cim": cim or ""
    })


@role_required(['operator', 'admin'])
def operator_dashboard(request):
    felhasznalo = request.session.get('felhasznalonev')
    today = date.today()

    
    mai_lejelentesek = Lejelentes.objects.filter(
        felhasznalo__felhasznalonev=felhasznalo,
        datum__date=today
    ).count()

    
    jo_db_ma = Lejelentes.objects.filter(
        felhasznalo__felhasznalonev=felhasznalo,
        datum__date=today
    ).aggregate(Sum('jo_db'))['jo_db__sum'] or 0

    
    selejt_ma = Lejelentes.objects.filter(
        felhasznalo__felhasznalonev=felhasznalo,
        datum__date=today
    ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0

    
    aktiv_gyartasok = GyartasFej.objects.exclude(statusz='lezart').count()

    
    folyamatban = GyartasFej.objects.filter(
        statusz='engedelyezett',
        lejelentes__isnull=False
    ).distinct().count()

    
    lezart = GyartasFej.objects.filter(statusz='lezart').count()

    return render(request, 'main/operator_dashboard.html', {
        'mai_lejelentesek': mai_lejelentesek,
        'jo_db_ma': jo_db_ma,
        'selejt_ma': selejt_ma,
        'aktiv_gyartasok': aktiv_gyartasok,
        'folyamatban': folyamatban,
        'lezart': lezart,
    })


from django.db.models import Sum, Count
from datetime import date, timedelta

@role_required(['vezeto', 'admin'])
def vezeto_dashboard(request):
    today = date.today()
    week_start = today - timedelta(days=today.weekday()) 

    jo_ma = Lejelentes.objects.filter(
        datum__date=today
    ).aggregate(Sum('jo_db'))['jo_db__sum'] or 0

    
    selejt_ma = Lejelentes.objects.filter(
        datum__date=today
    ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0

    
    jo_heti = Lejelentes.objects.filter(
        datum__date__gte=week_start
    ).aggregate(Sum('jo_db'))['jo_db__sum'] or 0

    
    selejt_heti = Lejelentes.objects.filter(
        datum__date__gte=week_start
    ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0

    
    if jo_ma + selejt_ma > 0:
        selejt_arany = round((selejt_ma / (jo_ma + selejt_ma)) * 100, 2)
    else:
        selejt_arany = 0

    

    
    top_jo = Lejelentes.objects.filter(
    felhasznalo__szerepkor='operator'
).values('felhasznalo__felhasznalonev') \
 .annotate(osszes_jo=Sum('jo_db')) \
 .order_by('-osszes_jo')[:5]


    
    top_selejt = Lejelentes.objects.filter(
    felhasznalo__szerepkor='operator'
).values('felhasznalo__felhasznalonev') \
 .annotate(osszes_selejt=Sum('selejt_db')) \
 .order_by('-osszes_selejt')[:5]


    
    top_aktiv = Lejelentes.objects.filter(
    felhasznalo__szerepkor='operator'
).values('felhasznalo__felhasznalonev') \
 .annotate(db=Count('lejelentes_id')) \
 .order_by('-db')[:5]



    

    figyelmeztetesek = []

    
    if selejt_arany > 10:
        figyelmeztetesek.append(f"Magas selejtarány ma: {selejt_arany}%")

    
    regota_folyamatban = GyartasFej.objects.filter(
        statusz='engedelyezett',
        letrehozas_datuma__date__lt=today - timedelta(days=3)
    )
    if regota_folyamatban.exists():
        figyelmeztetesek.append("Vannak 3 napnál régebb óta folyamatban lévő gyártások!")

    
    recept_hiany = GyartasFej.objects.filter(
        statusz='engedelyezett',
        kesztermek_cikkszam__receptfej__isnull=True
    )
    if recept_hiany.exists():
        figyelmeztetesek.append("Egyes engedélyezett gyártásokhoz nincs recept!")


    return render(request, 'main/vezeto_dashboard.html', {
        
        'jo_ma': jo_ma,
        'selejt_ma': selejt_ma,
        'jo_heti': jo_heti,
        'selejt_heti': selejt_heti,
        'selejt_arany': selejt_arany,

        
        'top_jo': top_jo,
        'top_selejt': top_selejt,
        'top_aktiv': top_aktiv,

        
        'figyelmeztetesek': figyelmeztetesek,
    })

from django.db.models import Sum, Count
from datetime import date, timedelta
from login.models import Felhasznalo
from gyartas_app.models import GyartasFej, Lejelentes, Cikk, Muvelet

@role_required(['admin'])
def admin_dashboard(request):
    from datetime import datetime, date, time, timedelta
    from django.utils.timezone import make_aware
    from django.db.models import Sum, Count
    

    ALACSONY_KESZLET_KUSZOB = 50

    alacsony_keszlet = Keszlet.objects.filter(cikk__tipus='alapanyag',mennyiseg__lt=50)


    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    start_today = make_aware(datetime.combine(today, time.min))
    end_today = make_aware(datetime.combine(today, time.max))

    start_week = make_aware(datetime.combine(week_start, time.min))
    end_week = make_aware(datetime.combine(today, time.max))

    
    user_count = Felhasznalo.objects.count()
    gyartas_count = GyartasFej.objects.count()
    aktiv_gyartasok = GyartasFej.objects.exclude(statusz='lezart').count()
    lezart_gyartasok = GyartasFej.objects.filter(statusz='lezart').count()

    
    jo_ma = Lejelentes.objects.filter(
        datum__range=(start_today, end_today)
    ).aggregate(Sum('jo_db'))['jo_db__sum'] or 0

    selejt_ma = Lejelentes.objects.filter(
        datum__range=(start_today, end_today)
    ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0

    
    jo_heti = Lejelentes.objects.filter(
        datum__range=(start_week, end_week)
    ).aggregate(Sum('jo_db'))['jo_db__sum'] or 0

    selejt_heti = Lejelentes.objects.filter(
        datum__range=(start_week, end_week)
    ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0

    
    if jo_ma + selejt_ma > 0:
        selejt_arany = round((selejt_ma / (jo_ma + selejt_ma)) * 100, 2)
    else:
        selejt_arany = 0

    
    top_jo = (
        Lejelentes.objects.filter(felhasznalo__szerepkor='operator')
        .values("felhasznalo__felhasznalonev")
        .annotate(osszes_jo=Sum("jo_db"))
        .order_by("-osszes_jo")[:5]
    )

    top_selejt = (
        Lejelentes.objects.filter(felhasznalo__szerepkor='operator')
        .values("felhasznalo__felhasznalonev")
        .annotate(osszes_selejt=Sum("selejt_db"))
        .order_by("-osszes_selejt")[:5]
    )

    top_aktiv = (
        Lejelentes.objects.filter(felhasznalo__szerepkor='operator')
        .values("felhasznalo__felhasznalonev")
        .annotate(db=Count("lejelentes_id"))
        .order_by("-db")[:5]
    )

    
    top_partnerek = (
        GyartasFej.objects.values("partner__partner_nev")
        .annotate(db=Count("gyartas_id"))
        .order_by("-db")[:5]
    )

    top_partnerek_jo = (
        Lejelentes.objects.values("gyartas__partner__partner_nev")
        .annotate(osszes_jo=Sum("jo_db"))
        .order_by("-osszes_jo")[:5]
    )

    top_partnerek_selejt = (
        Lejelentes.objects.values("gyartas__partner__partner_nev")
        .annotate(osszes_selejt=Sum("selejt_db"))
        .order_by("-osszes_selejt")[:5]
    )

    return render(request, "main/admin_dashboard.html", {
        "user_count": user_count,
        "gyartas_count": gyartas_count,
        "aktiv_gyartasok": aktiv_gyartasok,
        "lezart_gyartasok": lezart_gyartasok,

        "jo_ma": jo_ma,
        "selejt_ma": selejt_ma,
        "jo_heti": jo_heti,
        "selejt_heti": selejt_heti,
        "selejt_arany": selejt_arany,

        "top_jo": top_jo,
        "top_selejt": top_selejt,
        "top_aktiv": top_aktiv,

        "top_partnerek": top_partnerek,
        "top_partnerek_jo": top_partnerek_jo,
        "top_partnerek_selejt": top_partnerek_selejt,
        "alacsony_keszlet": alacsony_keszlet,
    })




from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from gyartas_app.models import GyartasFej, Lejelentes, Partner

from login.models import Felhasznalo



@role_required(['vezeto', 'admin'])
def vezeto_gyartas_indit(request, id):
    gy = GyartasFej.objects.get(gyartas_id=id)

    
    try:
        recept = ReceptFej.objects.get(kesztermek_cikkszam=gy.kesztermek_cikkszam)
    except ReceptFej.DoesNotExist:
        return render(request, 'main/vezeto_gyartas_reszletek.html', {
            'gyartas': gy,
            'sorok': GyartasSor.objects.filter(gyartas=gy).order_by('sorrend'),
            'error': 'Ehhez a késztermékhez nincs recept létrehozva!'
        })

    sorok = ReceptSor.objects.filter(recept=recept)
    gyartando = gy.tervezett_mennyiseg

    
    hianyok = []

    for s in sorok:
        szukseges = s.mennyiseg * gyartando

        
        try:
            keszlet = Keszlet.objects.get(cikk=s.alapanyag_cikkszam)
        except Keszlet.DoesNotExist:
            hianyok.append(f"{s.alapanyag_cikkszam.megnevezes} – nincs készleten egyáltalán!")
            continue

        if keszlet.mennyiseg < szukseges:
            hiany = szukseges - keszlet.mennyiseg
            hianyok.append(f"{s.alapanyag_cikkszam.megnevezes} – hiányzik {hiany:.2f}")

    
    if hianyok:
        return render(request, 'main/vezeto_gyartas_reszletek.html', {
            'gyartas': gy,
            'sorok': GyartasSor.objects.filter(gyartas=gy).order_by('sorrend'),
            'error': "A gyártás nem indítható el, mert nincs elég alapanyag!",
            'hianyok': hianyok
        })

    
    gy.statusz = 'engedelyezett'
    gy.save()

    return redirect('vezeto_gyartasok')

def admin_keszlet(request):
    kesztermekek = Keszlet.objects.filter(cikk__tipus='kesztermek')
    alapanyagok = Keszlet.objects.filter(cikk__tipus='alapanyag')

    return render(request, 'main/admin_keszlet.html', {
        'kesztermekek': kesztermekek,
        'alapanyagok': alapanyagok
    })



@role_required(['admin'])
def admin_keszlet_uj(request):
    if request.method == "POST":
        cikk_id = request.POST.get("cikk")
        mennyiseg = Decimal(request.POST.get("mennyiseg"))

        from gyartas_app.models import Keszlet, Cikk

        cikk = Cikk.objects.get(cikkszam=cikk_id)   

        keszlet, created = Keszlet.objects.get_or_create(cikk=cikk)
        keszlet.mennyiseg += mennyiseg
        keszlet.save()

        return redirect("admin_keszlet")

    from gyartas_app.models import Cikk
    alapanyagok = Cikk.objects.filter(tipus="alapanyag")

    return render(request, "main/admin_keszlet_uj.html", {
        "alapanyagok": alapanyagok
    })

@role_required(['operator', 'admin'])
def operator_muvelet_lejelentes(request, sor_id):
    sor = GyartasSor.objects.get(gyartas_sor_id=sor_id)
    gyartas = sor.gyartas

    
    if sor.sorrend == 1:
        bemeno = gyartas.tervezett_mennyiseg
    else:
        elozo = GyartasSor.objects.get(
            gyartas=gyartas,
            sorrend=sor.sorrend - 1
        )
        bemeno = elozo.jo_db

    if request.method == 'POST':
        jo = int(request.POST['jo'])
        selejt = int(request.POST['selejt'])

        
        sor.jo_db = jo
        sor.selejt_db = selejt
        sor.save()

        
        Lejelentes.objects.create(
            gyartas=gyartas,
            gyartas_sor=sor,
            felhasznalo=Felhasznalo.objects.get(felhasznalonev=request.session['felhasznalonev']),
            bemeno_db=bemeno,
            jo_db=jo,
            selejt_db=selejt
        )

        
        utolso_sorrend = GyartasSor.objects.filter(gyartas=gyartas).count()

        if sor.sorrend == utolso_sorrend:
            
            gyartas.jo_mennyiseg = jo

            osszes_selejt = GyartasSor.objects.filter(
                gyartas=gyartas
            ).aggregate(Sum('selejt_db'))['selejt_db__sum'] or 0
            gyartas.selejt_mennyiseg = osszes_selejt
            gyartas.save()

        return redirect('operator_gyartas_reszletek', id=gyartas.gyartas_id)

    return render(request, 'main/operator_muvelet_lejelentes.html', {
        'sor': sor,
        'gyartas': gyartas,
        'bemeno': bemeno
    })



@role_required(['admin'])
def admin_keszlet_audit(request):
    mozgások = KeszletMozgas.objects.all().order_by('-datum')

    
    for m in mozgások:
        
        lejelentes = Lejelentes.objects.filter(
            gyartas=m.gyartas
        ).order_by('-datum').first()

        if lejelentes:
            m.felhasznalo_nev = lejelentes.felhasznalo.felhasznalonev
        else:
            m.felhasznalo_nev = "Ismeretlen"

    return render(request, 'main/admin_keszlet_audit.html', {
        'mozgások': mozgások
    })

