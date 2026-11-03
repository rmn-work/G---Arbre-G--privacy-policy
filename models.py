from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Personne(models.Model):
    SEXE_CHOICES = [('M', 'Homme'), ('F', 'Femme')]

    utilisateur = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    ajoute_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="contributions")
    date_creation = models.DateTimeField(auto_now_add=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    est_vivant = models.BooleanField(default=True)
    date_deces = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='famille_photos/', null=True, blank=True)
    pere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='enfants_pere')
    mere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='enfants_mere')

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def enfants(self):
        return Personne.objects.filter(models.Q(pere=self) | models.Q(mere=self))

    @property
    def fratrie(self):
        query = models.Q()
        if self.pere_id:
            query |= models.Q(pere_id=self.pere_id)
        if self.mere_id:
            query |= models.Q(mere_id=self.mere_id)
        if not query:
            return Personne.objects.none()
        return Personne.objects.filter(query).exclude(id=self.id).distinct()

    @property
    def oncles_et_tantes(self):
        oncles_tantes = []
        if self.pere:
            oncles_tantes.extend(self.pere.fratrie)
        if self.mere:
            oncles_tantes.extend(self.mere.fratrie)
        return oncles_tantes

    @property
    def cousins(self):
        cousins_ids = []
        for oncle_tante in self.oncles_et_tantes:
            # Récupérer tous les enfants de cet oncle / cette tante
            enfants = Personne.objects.filter(models.Q(pere=oncle_tante) | models.Q(mere=oncle_tante))
            cousins_ids.extend(enfants.values_list('id', flat=True))
        return Personne.objects.filter(id__in=cousins_ids)


    def obtenir_relation(self, autre_personne):
        if self == autre_personne: return "Moi"
        if autre_personne == self.pere: return "Père"
        if autre_personne == self.mere: return "Mère"
        if self == autre_personne.pere: return "Fils" if self.sexe == 'M' else "Fille"
        if self.pere == autre_personne.pere and self.mere == autre_personne.mere:
            return "Frère" if self.sexe == 'M' else "Sœur"
        for parent in [autre_personne.pere, autre_personne.mere]:
            if parent and (parent.pere == self.pere or parent.mere == self.mere):
                return "Neveu" if self.sexe == 'M' else "Nièce"
        if self.pere and autre_personne.pere:
            if self.pere.pere == autre_personne.pere.pere:
                return "Cousin(e)"

        return "Parent éloigné"


class Anecdote(models.Model):
    personne_concernee = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='anecdotes')
    auteur = models.ForeignKey(Personne, on_delete=models.SET_NULL, null=True, related_name='anecdotes_ecrites')
    contenu = models.TextField()
    contenu_en = models.TextField(blank=True, null=True)  # Champ pour la version anglaise
    langue_originale = models.CharField(max_length=10, default='fr')
    date_creation = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.contenu:
            from .translation_service import traduire_texte
            self.contenu_en = traduire_texte(self.contenu, 'en')
        super().save(*args, **kwargs)


class CommentairePhoto(models.Model):
    photo = models.ForeignKey(PhotoFamille, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    texte = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_creation']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur photo {self.photo.id}"