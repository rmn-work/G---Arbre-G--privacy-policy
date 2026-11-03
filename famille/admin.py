from django.contrib import admin
from .models import Personne, PhotoSouvenir

class PhotoSouvenirInline(admin.TabularInline):
    model = PhotoSouvenir
    extra = 1

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'sexe', 'statut_matrimonial', 'est_vivant')
    list_filter = ('sexe', 'statut_matrimonial', 'est_vivant')
    search_fields = ('nom', 'prenom', 'profession', 'lieux_de_vie')
    inlines = [PhotoSouvenirInline]

@admin.register(PhotoSouvenir)
class PhotoSouvenirAdmin(admin.ModelAdmin):
    list_display = ('personne', 'legende', 'date_prise')
    search_fields = ('personne__prenom', 'personne__nom', 'legende')
    list_filter = ('date_prise',)