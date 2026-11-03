from django.contrib.auth.models import User
from famille.models import Anecdote, CommentairePhoto, Personne, PhotoFamille
from rest_framework import serializers


class MembreSerializer(serializers.ModelSerializer):

  class Meta:
    model = Personne
    fields = '__all__'


class AnecdoteSerializer(serializers.ModelSerializer):

  class Meta:
    model = Anecdote
    fields = ['personne', 'contenu', 'langue_originale']


class CommentairePhotoSerializer(serializers.ModelSerializer):
  auteur_nom = serializers.CharField(source='auteur.username', read_only=True)
  date_formatee = serializers.SerializerMethodField()

  class Meta:
    model = CommentairePhoto
    fields = [
        'id', 'photo', 'auteur_nom', 'texte', 'date_creation', 'date_formatee', 'utilisateurs_mentions', 'date_creation',
    ]
    read_only_fields = ['auteur_nom', 'photo']


  def get_date_formatee(self, obj):
    return obj.date_creation.strftime('%d/%m/%Y à %H:%M')


class PhotoFamilleSerializer(serializers.ModelSerializer):
  ajoute_par_nom = serializers.CharField(
      source='ajoute_par.username', read_only=True
  )
  commentaires = CommentairePhotoSerializer(many=True, read_only=True)

  class Meta:
    model = PhotoFamille
    fields = [
        'id', 'image', 'legende', 'ajoute_par_nom', 'utilisateurs_taguees', 'commentaires', 'date_ajout',
    ]
    read_only_fields = ['ajoute_par_nom', 'date_ajout']