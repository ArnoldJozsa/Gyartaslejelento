from django.urls import path
from . import views

from django.urls import path
from .views import nav_lekerdezes

urlpatterns = [
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('operator/', views.operator_dashboard, name='operator_dashboard'),
    path('operator/gyartasok/', views.operator_gyartasok, name='operator_gyartasok'),
    path('operator/riport/', views.operator_riport, name='operator_riport'),
    path('operator/riport/export/', views.operator_riport_export, name='operator_riport_export'),
    path('vezeto/', views.vezeto_dashboard, name='vezeto_dashboard'),
    path('nincs-jogosultsag/', views.nincs_jogosultsag, name='nincs_jogosultsag'),
    path('operator/riport/pdf/', views.operator_riport_pdf, name='operator_riport_pdf'),
    path('vezeto/gyartasok/', views.vezeto_gyartasok, name='vezeto_gyartasok'),
path('vezeto/gyartas/<int:id>/indit/', views.vezeto_gyartas_indit, name='vezeto_gyartas_indit'),
path('vezeto/gyartas/<int:id>/lezar/', views.vezeto_gyartas_lezar, name='vezeto_gyartas_lezar'),
path('admin-panel/cikkek/', views.admin_cikkek, name='admin_cikkek'),
path('admin-panel/cikkek/uj/', views.admin_cikk_uj, name='admin_cikk_uj'),
# --- MŰVELETEK ---
path('admin-panel/muveletek/', views.admin_muveletek, name='admin_muveletek'),
path('admin-panel/muveletek/uj/', views.admin_muvelet_uj, name='admin_muvelet_uj'),
path('admin-panel/muveletek/<int:id>/szerkeszt/', views.admin_muvelet_szerkeszt, name='admin_muvelet_szerkeszt'),
path('admin-panel/muveletek/<int:id>/torol/', views.admin_muvelet_torol, name='admin_muvelet_torol'),
# --- RECEPTÚRÁK ---
path('admin-panel/recept/', views.admin_recept_lista, name='admin_recept_lista'),
path('admin-panel/recept/uj/', views.admin_recept_uj, name='admin_recept_uj'),
path('admin-panel/recept/<int:id>/', views.admin_recept_sorok, name='admin_recept_sorok'),
path('admin-panel/recept/<int:id>/torol/', views.admin_recept_torol, name='admin_recept_torol'),

# --- GYÁRTÁS LÉTREHOZÁSA ---
path('vezeto/gyartas/uj/', views.vezeto_gyartas_uj, name='vezeto_gyartas_uj'),

# --- OPERÁTOR LEJELENTÉS ---
path('operator/gyartas/<int:id>/', views.operator_gyartas_reszletek, name='operator_gyartas_reszletek'),
path('operator/gyartas/<int:id>/lejelentes/', views.operator_lejelentes, name='operator_lejelentes'),



# --- VEZETŐI GYÁRTÁSOK ---
path('vezeto/gyartasok/', views.vezeto_gyartasok, name='vezeto_gyartasok'),
path('vezeto/gyartas/<int:id>/', views.vezeto_gyartas_reszletek, name='vezeto_gyartas_reszletek'),
path('vezeto/gyartas/<int:id>/indit/', views.vezeto_gyartas_indit, name='vezeto_gyartas_indit'),
path('vezeto/gyartas/<int:id>/lezar/', views.vezeto_gyartas_lezar, name='vezeto_gyartas_lezar'),
path('vezeto/gyartas/<int:id>/lejelentes/', views.vezeto_gyartas_lejelentes),


# --- OPERÁTORI GYÁRTÁSOK ---
path('operator/gyartasok/', views.operator_gyartasok, name='operator_gyartasok'),

# --- PARTNEREK ---
path('admin-panel/partnerek/', views.admin_partnerek, name='admin_partnerek'),
path('admin-panel/partnerek/uj/', views.admin_partner_uj, name='admin_partner_uj'),
path('admin-panel/partnerek/<int:id>/szerkeszt/', views.admin_partner_szerkeszt, name='admin_partner_szerkeszt'),
path('admin-panel/partnerek/<int:id>/torol/', views.admin_partner_torol, name='admin_partner_torol'),

path('nav-lekerdezes/<str:adoszam>/', views.nav_lekerdezes, name='nav_lekerdezes'),
path("admin-panel/keszlet/", views.admin_keszlet, name="admin_keszlet"),
path("admin-panel/keszlet/uj/", views.admin_keszlet_uj, name="admin_keszlet_uj"),
path('operator/gyartas/sor/<int:sor_id>/lejelentes/', views.operator_muvelet_lejelentes),
path('vezeto/keszlet/audit/', views.admin_keszlet_audit, name='admin_keszlet_audit'),







]
