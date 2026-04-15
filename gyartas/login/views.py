from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from login.models import Felhasznalo

def login_view(request):
    if request.method == "POST":
        azonosito = request.POST.get("felhasznalonev")
        jelszo = request.POST.get("jelszo")

        try:
            user = Felhasznalo.objects.get(vonalkod=azonosito)

            request.session['user_id'] = user.felhasznalo_id
            request.session['szerepkor'] = user.szerepkor
            request.session['is_authenticated'] = True
            request.session['felhasznalonev'] = user.felhasznalonev

            
            if user.szerepkor == 'admin':
                return redirect('/admin-panel/')
            elif user.szerepkor == 'vezeto':
                return redirect('/vezeto/')
            else:
                return redirect('/operator/')

        except Felhasznalo.DoesNotExist:
            pass

        try:
            user = Felhasznalo.objects.get(felhasznalonev=azonosito)
        except Felhasznalo.DoesNotExist:
            return render(request, 'login/login.html', {'error': 'Hibás felhasználónév vagy vonalkód'})

        if check_password(jelszo, user.jelszo):

            request.session['user_id'] = user.felhasznalo_id
            request.session['szerepkor'] = user.szerepkor
            request.session['is_authenticated'] = True
            request.session['felhasznalonev'] = user.felhasznalonev

            if user.szerepkor == 'admin':
                return redirect('/admin-panel/')
            elif user.szerepkor == 'vezeto':
                return redirect('/vezeto/')
            else:
                return redirect('/operator/')

        else:
            return render(request, 'login/login.html', {'error': 'Hibás jelszó'})

    return render(request, 'login/login.html')


def logout_view(request):
    request.session.flush()  
    return redirect('/login/')
