from django.shortcuts import render, redirect
from functools import wraps

def sajat_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_authenticated') and request.session.get('felhasznalonev') == "adminuser":
            return view_func(request, *args, **kwargs)
        else:
            return redirect(f'/login/?next={request.path}')
    return wrapper

@sajat_login_required
def admin_home(request):
    return render(request, 'admin_panel/admin_panel.html')
