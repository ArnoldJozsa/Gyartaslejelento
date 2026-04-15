from django.urls import path
from . import views

urlpatterns = [
    path('gyartas/<int:gyartas_id>/lezaras/', views.gyartas_lezaras, name='gyartas_lezaras'),

]
