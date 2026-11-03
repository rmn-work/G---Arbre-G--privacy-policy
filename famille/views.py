import json
import re
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from .forms import MembreForm, AnecdoteForm, ProfilForm, PhotoFamilleForm
from .models import Personne, Anecdote, PhotoFamille, CommentairePhoto, NotificationAEnvoyer
from .serializers import MembreSerializer, AnecdoteSerializer
from .translation_service import traduire_texte
from .permissions import EstEditeurOuLectureSeule


def accueil(request):
    """
    Redirige l'utilisateur vers l'arbre s'il est connecté,
    sinon vers la page de connexion.
    """
    if request.user.is_authenticated:
        return redirect('accueil_arbre')
    return redirect('login')

class AnecdoteCreateView(APIView):
    """
    API pour la publication d'anecdotes depuis l'application mobile.
    """

    def post(self, request, *args, **kwargs):
        serializer = AnecdoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Anecdote publiée avec succès"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, EstEditeurOuLectureSeule])
def api_liste_membres(request):
    if request.method == 'GET':
        query = request.query_params.get('search', None)
        membres = Personne.objects.all()
        if query:
            membres = membres.filter(
                Q(prenom__icontains=query) |
                Q(nom__icontains=query) |
                Q(profession__icontains=query)
            )
        serializer = MembreSerializer(membres, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MembreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_evenements_du_mois(request):
    mois_actuel = timezone.now().month
    naissances = Personne.objects.filter(date_naissance__month=mois_actuel, est_vivant=True)
    mariages = Personne.objects.filter(date_mariage__month=mois_actuel)
    deces = Personne.objects.filter(date_deces__month=mois_actuel, est_vivant=False)
    data = {
        "mois": mois_actuel,
        "anniversaires_naissance": [
            {"id": p.id, "nom_complet": f"{p.prenom} {p.nom}", "jour": p.date_naissance.day,
             "age_celebre": timezone.now().year - p.date_naissance.year}
            for p in naissances
        ],
        "anniversaires_mariage": [
            {"id": p.id, "nom_complet": f"{p.prenom} {p.nom}", "jour": p.date_mariage.day,
             "annees_mariage": timezone.now().year - p.date_mariage.year}
            for p in mariages
        ],
        "commemorations_deces": [
            {"id": p.id, "nom_complet": f"{p.prenom} {p.nom}", "jour": p.date_deces.day,
             "annees_passees": timezone.now().year - p.date_deces.year}
            for p in deces
        ]
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_traduire_anecdote(request):
    texte = request.GET.get('texte', '')
    langue_cible = request.GET.get('cible', 'fr')
    if not texte:
        return JsonResponse({'erreur': 'Aucun texte fourni'}, status=400)
    texte_traduit = traduire_texte(texte, langue_cible)
    return JsonResponse({'texte_traduit': texte_traduit})


@api_view(['POST'])
@permission_classes([])
def api_inscription(request):
    code_secret = request.data.get('code_secret')
    username = request.data.get('username')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    if code_secret != 'GACUKUZI2026':
        return Response({'erreur': 'Le code secret de la famille est incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
    if not username or not password:
        return Response({'erreur': 'Le nom d’utilisateur et le mot de passe sont requis.'},
                        status=status.HTTP_400_BAD_REQUEST)
    if password != password_confirm:
        return Response({'erreur': 'Les mots de passe ne correspondent pas.'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'erreur': 'Ce nom d’utilisateur est déjà pris.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.create_user(username=username, password=password)
        return Response({'succes': 'Compte créé avec succès !'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'erreur': f'Une erreur est survenue : {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def exporter_arbre_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Livre_Famille.pdf"'
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Arbre Généalogique Familial", styles['Title']))
    elements.append(Paragraph("<br/>Liste des membres enregistrés", styles['Normal']))
    data = [['Prénom', 'Nom', 'Statut', 'Lieu de vie']]
    for membre in Personne.objects.all():
        data.append([
            membre.prenom,
            membre.nom,
            "Vivant" if membre.est_vivant else "🕊️",
            membre.lieux_de_vie or "N/A"
        ])
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(t)
    doc.build(elements)
    return response


def inscription(request):
    if request.method == 'POST':
        code_secret = request.POST.get('code_secret')
        form = UserCreationForm(request.POST)
        if code_secret != 'GACUKUZI2026':
            messages.error(request, "Le code secret de la famille est incorrect.")
        elif form.is_valid():
            form.save()
            messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'famille/inscription.html', {'form': form})


@login_required(login_url='login')
def mon_profil(request):
    personne, created = Personne.objects.get_or_create(utilisateur=request.user)

    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=personne)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('mon_profil')
    else:
        form = ProfilForm(instance=personne)

    return render(request, 'famille/profil.html', {'form': form, 'personne': personne})


@login_required(login_url='login')
def arbre_genealogique(request):
    membres = Personne.objects.all()
    nodes = []
    edges = []

    for m in membres:
        premiere_photo = m.souvenirs.order_by('date_prise').first()
        photo_url = premiere_photo.image.url if premiere_photo else '/static/images/default_avatar.png'

        rang = m.rang_dans_fratrie() if hasattr(m, 'rang_dans_fratrie') else None
        label_texte = f"{m.prenom} {m.nom}"
        if rang:
            label_texte += f"\n({rang})"

        statut = getattr(m, 'statut_matrimonial', 'Inconnu')
        titre_texte = f"Statut: {statut} | Né(e) le: {m.date_naissance}"
        if rang:
            titre_texte += f" | Rang: {rang}"

        nodes.append({
            'id': m.id,
            'label': label_texte,
            'title': titre_texte,
            'image': photo_url,
            'shape': 'circularImage'
        })

        if getattr(m, 'pere', None):
            edges.append({'from': m.pere.id, 'to': m.id, 'label': 'Père de', 'arrows': 'to'})
        if getattr(m, 'mere', None):
            edges.append({'from': m.mere.id, 'to': m.id, 'label': 'Mère de', 'arrows': 'to'})
        if getattr(m, 'conjoint', None):
            edges.append({'from': m.id, 'to': m.conjoint.id, 'label': 'Époux/se', 'arrows': ''})

    context = {
        'nodes_json': json.dumps(nodes),
        'edges_json': json.dumps(edges),
    }
    return render(request, 'famille/arbre.html', context)


def page_deconnexion(request):
    return render(request, 'famille/deconnecte.html')


def load_anecdotes(request, personne_id):
    personne = get_object_or_404(Personne, id=personne_id)
    anecdotes = personne.anecdotes.all() if hasattr(personne, 'anecdotes') else []
    anecdotes_list = [{
        'id': anc.id,
        'contenu': anc.contenu,
        'signataire': anc.get_signataire_formatte() if hasattr(anc, 'get_signataire_formatte') else "Anonyme",
        'date': anc.date_creation.strftime("%d/%m/%Y"),
        'langue_code': getattr(anc, 'langue_originale', 'fr')
    } for anc in anecdotes]
    return JsonResponse({'anecdotes': anecdotes_list})


@login_required
def raconter_anecdote(request, personne_id):
    personne = get_object_or_404(Personne, pk=personne_id)

    if request.method == 'POST':
        form = AnecdoteForm(request.POST)
        if form.is_valid():
            anecdote = form.save(commit=False)
            anecdote.personne = personne
            anecdote.auteur = request.user
            anecdote.save()
            messages.success(request, f"Anecdote ajoutée sur {personne} !")
            return redirect('accueil_arbre')
    else:
        form = AnecdoteForm(initial={'personne_id': personne_id})

    return render(request, 'famille/raconter_anecdote.html', {
        'form': form,
        'personne': personne
    })


def load_relations(request, personne_id):
    try:
        personne = Personne.objects.get(id=personne_id)
    except Personne.DoesNotExist:
        return JsonResponse({"erreur": "Personne introuvable"}, status=404)

    pere = personne.pere
    mere = personne.mere

    fratrie = set()
    if pere:
        fratrie.update(Personne.objects.filter(pere=pere).exclude(id=personne.id))
    if mere:
        fratrie.update(Personne.objects.filter(mere=mere).exclude(id=personne.id))

    oncles_tantes_data = []

    def ajouter_oncles_tantes(parent, cote):
        if not parent: return

        sibs = set()
        if parent.pere:
            sibs.update(Personne.objects.filter(pere=parent.pere).exclude(id=parent.id))
        if parent.mere:
            sibs.update(Personne.objects.filter(mere=parent.mere).exclude(id=parent.id))

        for p in sibs:
            oncles_tantes_data.append({
                "nom": f"{p.prenom} {p.nom}",
                "relation": "Oncle" if getattr(p, 'sexe', 'M') == 'M' else "Tante",
                "cote": cote
            })

    ajouter_oncles_tantes(pere, "paternel")
    ajouter_oncles_tantes(mere, "maternel")

    data = {
        "nom_complet": f"{personne.prenom} {personne.nom}",
        "parents": {
            "pere": f"{pere.prenom} {pere.nom}" if pere else None,
            "mere": f"{mere.prenom} {mere.nom}" if mere else None,
        },
        "fratrie": [f"{p.prenom} {p.nom}" for p in fratrie],
        "oncles_tantes": oncles_tantes_data,
        "cousins": []
    }

    return JsonResponse(data)


@login_required
def ajouter_enfant(request, parent_id):
    parent = get_object_or_404(Personne, id=parent_id)

    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES)
        if form.is_valid():
            enfant = form.save(commit=False)
            if getattr(parent, 'sexe', None) == 'M' or getattr(parent, 'genre', None) == 'M':
                enfant.pere = parent
            else:
                enfant.mere = parent

            enfant.save()
            messages.success(request, f"L'enfant {enfant.prenom} {enfant.nom} a bien été ajouté à l'arbre !")
            return redirect('accueil_arbre')
    else:
        form = MembreForm(initial={'nom': parent.nom})

    return render(request, 'famille/ajouter_enfant.html', {
        'form': form,
        'parent': parent
    })


@login_required
def album_famille(request):
    photos = PhotoFamille.objects.all()

    if request.method == 'POST':
        form = PhotoFamilleForm(request.POST, request.FILES)
        if form.is_valid():
            nouvelle_photo = form.save(commit=False)
            nouvelle_photo.ajoute_par = request.user
            nouvelle_photo.save()
            messages.success(request, "Votre photo a été ajoutée à l'album avec succès !")
            return redirect('album_famille')
    else:
        form = PhotoFamilleForm()

    return render(request, 'famille/album.html', {
        'photos': photos,
        'form': form
    })

def ajouter_commentaire_photo(request, photo_id):
  if request.method == 'POST':
    photo = PhotoFamille.objects.get(id=photo_id)
    texte = request.POST.get('texte_commentaire', '')
    auteur = request.user
    commentaire = CommentairePhoto.objects.create(
        photo=photo, auteur=auteur, texte=texte
    )
    usernames_trouves = re.findall(r'@(\w+)', texte)

    if usernames_trouves:
      utilisateurs_cibles = User.objects.filter(
          username__in=usernames_trouves
      )

      for utilisateur in utilisateurs_cibles:
        if utilisateur != auteur:
          commentaire.utilisateurs_mentions.add(utilisateur)
          NotificationAEnvoyer.objects.create(
              titre=f'Nouveau tag de @{auteur.username}',
              contenu=(
                  f"@{auteur.username} vous a mentionné dans un commentaire sur"
                  ' l’album de famille.'
              ),
          )

  return redirect('album_famille')