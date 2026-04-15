from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from login import views as login_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('gyartas/', include('gyartas_app.urls')),
    path('login/', include('login.urls')),

    path('', lambda request: redirect('login')),   
    path('', include('main.urls')),

    path('logout/', login_views.logout_view, name='logout'),
]
