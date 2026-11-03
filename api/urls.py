from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('membres/', views.MembreListView.as_view(), name='membre-list'),
    path('album/', views.PhotoFamilleListCreate.as_view(), name='api_album_famille'),
    path('album/<int:photo_id>/commentaires/', views.CommentaireListCreate.as_view(), name='api_photo_commentaires'),
]