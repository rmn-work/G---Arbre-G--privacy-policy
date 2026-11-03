from django import forms
from .models import Personne, Anecdote, PhotoFamille
from django.utils.translation import gettext_lazy as _


class MembreForm(forms.ModelForm):
    code_invitation = forms.CharField(
        label=_("Code Secret de la Famille"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Entrez le code secret')}),
        required=True
    )

    class Meta:
        model = Personne
        fields = [
            'nom', 'prenom', 'sexe', 'statut_matrimonial',
            'date_naissance', 'est_vivant', 'date_deces', 'biographie',
            'pere', 'mere', 'conjoint'
        ]

        labels = {
            'nom': _('Nom'),
            'prenom': _('Prénom'),
            'sexe': _('Sexe'),
            'statut_matrimonial': _('Statut matrimonial'),
            'date_naissance': _('Date de naissance'),
            'est_vivant': _('Est vivant'),
            'date_deces': _('Date de décès'),
            'biographie': _('Biographie'),
            'pere': _('Père'),
            'mere': _('Mère'),
            'conjoint': _('Conjoint(e)'),
        }

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'statut_matrimonial': forms.Select(attrs={'class': 'form-select'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_deces': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'biographie': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pere': forms.Select(attrs={'class': 'form-select'}),
            'mere': forms.Select(attrs={'class': 'form-select'}),
            'conjoint': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_code_invitation(self):
        code = self.cleaned_data.get('code_invitation')
        if code != "GACUKUZI2026":
            raise forms.ValidationError(_("Le code secret est incorrect. Vous ne pouvez pas rejoindre cet arbre."))
        return code


class AnecdoteForm(forms.ModelForm):
    personne_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Anecdote
        fields = ['contenu', 'langue_originale']

        labels = {
            'contenu': _('Contenu de l\'anecdote'),
            'langue_originale': _('Langue originale'),
        }

        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': _('Racontez une petite histoire sur cette personne...'),
                'style': 'resize: vertical;'
            }),
            'langue_originale': forms.Select(attrs={'class': 'form-select'}),
        }


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['nom', 'prenom', 'photo_profil', 'biographie', 'profession', 'lieux_de_vie']

        labels = {
            'nom': _('Nom'),
            'prenom': _('Prénom'),
            'photo_profil': _('Photo de profil'),
            'biographie': _('Biographie'),
            'profession': _('Profession'),
            'lieux_de_vie': _('Lieux de vie'),
        }

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_profil': forms.FileInput(attrs={'class': 'form-control'}),
            'biographie': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'lieux_de_vie': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PhotoFamilleForm(forms.ModelForm):
    class Meta:
        model = PhotoFamille
        fields = ['image', 'legende']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
            'legende': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dites un mot sur cette photo...'}),
        }