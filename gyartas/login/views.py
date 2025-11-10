from django.shortcuts import render, redirect
import pymysql

def login_view(request):
    if request.method == "POST":
        felhasznalonev = request.POST.get("felhasznalonev")
        jelszo = request.POST.get("jelszo")
        next_url = request.POST.get("next") or '/main'

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='12345',
            database='gyartas_db'
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM felhasznalok WHERE felhasznalonev=%s AND jelszo=%s",
            (felhasznalonev, jelszo)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            request.session['felhasznalonev'] = felhasznalonev
            request.session['is_authenticated'] = True

            if felhasznalonev == "adminuser":
                return redirect('/admin-panel/')
            else:
                return redirect(next_url)
        else:
            return render(request, 'login/login.html', {
                'error': 'Hibás felhasználónév vagy jelszó',
                'next': next_url
            })

    next_url = request.GET.get('next', '/main')
    return render(request, 'login/login.html', {'next': next_url})
