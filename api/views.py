from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from famille.models import Personne, PhotoFamille
from famille.serializers import MembreSerializer, PhotoFamilleSerializer
from famille.models import CommentairePhoto
from famille.serializers import CommentairePhotoSerializer


@login_required
def vue_arbre_genealogique(request):
    return render(request, 'famille/arbre.html', {})


@login_required
def raconter_anecdote(request, personne_id):
    personne = get_object_or_404(Personne, id=personne_id)
    return render(request, 'famille/raconter_anecdote.html', {'personne': personne})


@api_view(['POST'])
def inscription_famille(request):
    email = request.data.get('email')
    password = request.data.get('password')
    nom = request.data.get('nom')


    if User.objects.filter(username=email).exists():
        return Response({"error": "Cet email est déjà utilisé"}, status=400)


    user = User.objects.create_user(username=email, email=email, password=password)
    Personne.objects.create(user=user, nom=nom, prenom="")
    return Response({"message": "Compte créé avec succès !"}, status=201)


class MembreListView(generics.ListAPIView):
    queryset = Personne.objects.all()
    serializer_class = MembreSerializer
    permission_classes = [AllowAny]


def load_relations(request, personne_id):

    try:
        personne = Personne.objects.get(id=personne_id)

    except Personne.DoesNotExist:

        return JsonResponse({"erreur": "Personne introuvable"}, status=404)

    data = {
        "nom_complet": f"{personne.prenom} {personne.nom}",
        "parents": {
            "pere": f"{personne.pere.prenom} {personne.pere.nom}" if personne.pere else None,
            "mere": f"{personne.mere.prenom} {personne.mere.nom}" if personne.mere else None,
        },

        "fratrie": [f"{p.prenom} {p.nom}" for p in personne.fratrie],
        "oncles_tantes": [
            {
                "nom": f"{ot.prenom} {ot.nom}",
                "relation": "Oncle" if ot.sexe == 'M' else "Tante",
                "cote": "paternel" if (personne.pere and ot in personne.pere.fratrie) else "maternel"
            }
            for ot in personne.oncles_et_tantes
        ],

        "cousins": [f"{c.prenom} {c.nom}" for c in personne.cousins]
    }

    return JsonResponse(data)


class PhotoFamilleListCreate(generics.ListCreateAPIView):
    queryset = PhotoFamille.objects.all()
    serializer_class = PhotoFamilleSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(ajoute_par=self.request.user)


class CommentaireListCreate(generics.ListCreateAPIView):
    serializer_class = CommentairePhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return CommentairePhoto.objects.filter(photo_id=self.kwargs['photo_id'])

    def perform_create(self, serializer):
        photo = get_object_or_404(PhotoFamille, id=self.kwargs['photo_id'])
        serializer.save(auteur=self.request.user, photo=photo)