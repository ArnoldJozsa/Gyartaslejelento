from django.shortcuts import render, redirect
import pymysql

def login_view(request):
    if request.method == "POST":
        felhasznalonev = request.POST.get("felhasznalonev")
        jelszo = request.POST.get("jelszo")

        # Kapcsolódás a MySQL adatbázishoz
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='12345',  # ide a MySQL jelszavad
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
            # Ellenőrizzük, hogy admin vagy sima felhasználó
            if felhasznalonev == "adminuser":
                return redirect('admin_home')  # admin felület
            else:
                return redirect('main')  # main oldal
        else:
            return render(request, 'login/login.html', {'error': 'Hibás felhasználónév vagy jelszó'})

    return render(request, 'login/login.html')
