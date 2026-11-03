from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import models
from famille.models import PhotoFamille
from django.contrib.auth.models import User

class Personne(models.Model):
    SEXE_CHOICES = [
        ('M', _('Masculin')),
        ('F', _('Féminin')),
    ]


    STATUT_CHOICES = [
        ('CELIBATAIRE', _('Célibataire')),
        ('MARIE', _('Marié(e)')),
        ('VEUF', _('Veuf/Veuve')),
        ('ENFANT', _('Enfant')),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    statut_matrimonial = models.CharField(max_length=20, choices=STATUT_CHOICES)
    date_naissance = models.DateField()
    est_vivant = models.BooleanField(default=True)
    date_deces = models.DateField(null=True, blank=True)
    biographie = models.TextField(blank=True)
    pere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='enfants_du_pere')
    mere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='enfants_de_la_mere')
    conjoint = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='partenaire')

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class PhotoPersonne(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='galerie_photos')
    image = models.ImageField(upload_to='famille_photos/')
    date_prise = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        date_str = self.date_prise if self.date_prise else _("Date inconnue")
        return f"Photo de {self.personne.prenom} - {date_str}"


class Anecdote(models.Model):
    LANGUES_CHOICES = [
        ('fr', _('Français')),
        ('en', _('Anglais')),
    ]

    personne_concernee = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='anecdotes')
    auteur = models.ForeignKey(Personne, on_delete=models.SET_NULL, null=True, related_name='anecdotes_contees')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    langue_originale = models.CharField(
        max_length=2,
        default='fr',
        choices=LANGUES_CHOICES
    )

    class Meta:
        ordering = ['-date_creation']

    def get_signataire_formatte(self):
        """Génère la signature @PrenomNom de l'auteur."""
        if self.auteur:
            return f"@{self.auteur.prenom}{self.auteur.nom}"
        return "@MembreInconnu"

    def __str__(self):
        auteur_nom = self.auteur if self.auteur else _("Inconnu")
        return f"Anecdote sur {self.personne_concernee} par {auteur_nom}"