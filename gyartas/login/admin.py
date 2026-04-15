from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Felhasznalo

class FelhasznaloAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # Ha a jelszó változott, hash-eljük
        if 'jelszo' in form.cleaned_data:
            raw_password = form.cleaned_data['jelszo']
            if not raw_password.startswith('pbkdf2_sha256'):
                obj.jelszo = make_password(raw_password)
        super().save_model(request, obj, form, change)

admin.site.register(Felhasznalo, FelhasznaloAdmin)
