from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def admin_home(request):
    return render(request, 'admin_panel/admin_panel.html')
# Create your views here.
