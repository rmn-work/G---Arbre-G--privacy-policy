from django.contrib import admin
from .models import Personne

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'date_creation', 'ajoute_par', 'est_vivant')
    list_filter = ('est_vivant', 'sexe')
    search_fields = ('nom', 'prenom')
    readonly_fields = ('date_creation', 'ajoute_par')

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Si c'est une nouvelle création
            obj.ajoute_par = request.user
        super().save_model(request, obj, form, change)