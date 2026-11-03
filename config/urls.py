from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from famille.views import arbre_genealogique, inscription, mon_profil, page_deconnexion
from famille import views as famille_views
from api import views as api_views
from api import views
from famille.views import AnecdoteCreateView
from famille import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('profil/', mon_profil, name='mon_profil'),
    path('bye/', page_deconnexion, name='deconnexion_reussie'),
    path('famille/ajax/load_anecdotes/<int:personne_id>/', views.load_anecdotes, name='load_anecdotes'),
    path('famille/ajax/load_relations/<int:personne_id>/', views.load_relations, name='load_relations'),
    path('famille/raconter_anecdote/<int:personne_id>/', views.raconter_anecdote, name='raconter_anecdote'),
    path('api/anecdote/publier/', AnecdoteCreateView.as_view(), name='publier_anecdote'),
    path('famille/inscription/', views.inscription, name='inscription'),
    path('famille/ajouter_enfant/<int:parent_id>/', views.ajouter_enfant, name='ajouter_enfant'),
    path('famille/album/', views.album_famille, name='album_famille'),
]

urlpatterns += i18n_patterns(
    path('', auth_views.LoginView.as_view(template_name='famille/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('arbre/', arbre_genealogique, name='accueil_arbre'),
    path('inscription/', inscription, name='inscription'),
    prefix_default_language=True,
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)