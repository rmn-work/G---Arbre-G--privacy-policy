from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Personne(models.Model):
  SEXE_CHOICES = [('M', 'Homme'), ('F', 'Femme')]
  STATUT_CHOICES = [
      ('CELIBATAIRE', 'Célibataire'),
      ('MARIE', 'Marié(e)'),
      ('DIVORCE', 'Divorcé(e)'),
      ('VEUF', 'Veuf/Veuve'),
      ('ENFANT', 'Enfant'),
  ]

  utilisateur = models.OneToOneField(
      User, on_delete=models.SET_NULL, null=True, blank=True
  )
  ajoute_par = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='contributions',
  )
  date_creation = models.DateTimeField(auto_now_add=True)
  nom = models.CharField(max_length=100)
  prenom = models.CharField(max_length=100)
  sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
  statut_matrimonial = models.CharField(
      max_length=20, choices=STATUT_CHOICES, default='CELIBATAIRE'
  )
  date_naissance = models.DateField(null=True, blank=True)
  date_mariage = models.DateField(null=True, blank=True)
  profession = models.CharField(max_length=150, blank=True, null=True)
  lieux_de_vie = models.CharField(max_length=250, blank=True, null=True)
  biographie = models.TextField(blank=True, null=True)
  photo_profil = models.ImageField(
      upload_to='photos_profil/', blank=True, null=True
  )
  est_vivant = models.BooleanField(default=True)
  date_deces = models.DateField(
      null=True, blank=True, verbose_name='Date de décès'
  )

  pere = models.ForeignKey(
      'self',
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='enfants_pere',
  )
  mere = models.ForeignKey(
      'self',
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='enfants_mere',
  )
  conjoint = models.ForeignKey(
      'self',
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='partenaire',
  )

  def __str__(self):
    return f'{self.prenom} {self.nom}'

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


class PhotoSouvenir(models.Model):
  personne = models.ForeignKey(
      Personne, on_delete=models.CASCADE, related_name='souvenirs'
  )
  image = models.ImageField(upload_to='souvenirs/%Y/%m/')
  legende = models.CharField(max_length=200, blank=True, null=True)
  date_prise = models.DateField(blank=True, null=True)
  date_ajout = models.DateTimeField(auto_now_add=True)


class Anecdote(models.Model):
  LANGUES_CHOICES = [
      ('fr', 'Français'),
      ('en', 'Anglais'),
  ]

  personne_concernee = models.ForeignKey(
      Personne, on_delete=models.CASCADE, related_name='anecdotes'
  )
  auteur = models.ForeignKey(
      Personne,
      on_delete=models.SET_NULL,
      null=True,
      related_name='anecdotes_contees',
  )
  contenu = models.TextField()
  date_creation = models.DateTimeField(auto_now_add=True)
  langue_originale = models.CharField(
      max_length=2, default='fr', choices=LANGUES_CHOICES
  )

  class Meta:
    ordering = ['-date_creation']

  def __str__(self):
    auteur_nom = self.auteur if self.auteur else 'Inconnu'
    return f'Anecdote sur {self.personne_concernee} par {auteur_nom}'


class NotificationAEnvoyer(models.Model):
  titre = models.CharField(max_length=150)
  contenu = models.TextField()
  cree_le = models.DateTimeField(auto_now_add=True)
  est_envoye = models.BooleanField(default=False)


@receiver(post_save, sender=Personne)
def notifier_famille(sender, instance, created, **kwargs):
  if created:
    print(f'Notification: {instance.prenom} {instance.nom} ajouté.')


class PhotoFamille(models.Model):
  image = models.ImageField(upload_to='album_famille/%Y/%m/')
  legende = models.CharField(
      max_length=255, blank=True, null=True, verbose_name='Légende'
  )
  ajoute_par = models.ForeignKey(
      User,
      on_delete=models.SET_NULL,
      null=True,
      related_name='photos_postees',
  )
  utilisateurs_taguees = models.ManyToManyField(
      User, related_name='photos_taguees', blank=True
  )
  date_ajout = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-date_ajout']

  def __str__(self):
    return f'Photo ajoutée par {self.ajoute_par} le {self.date_ajout.strftime("%d/%m/%Y")}'


class CommentairePhoto(models.Model):
  photo = models.ForeignKey(
      PhotoFamille, on_delete=models.CASCADE, related_name='commentaires'
  )
  auteur = models.ForeignKey(User, on_delete=models.CASCADE)
  texte = models.TextField()
  utilisateurs_mentions = models.ManyToManyField(
      User, related_name='mentions_commentaires', blank=True
  )
  date_creation = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['date_creation']

  def __str__(self):
    return f'Commentaire de {self.auteur} sur photo {self.photo.id}'