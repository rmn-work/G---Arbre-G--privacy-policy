from modeltranslation.translator import register, TranslationOptions
from .models import Personne, Anecdote

@register(Personne)
class PersonneTranslationOptions(TranslationOptions):
    fields = ('profession', 'lieux_de_vie', 'biographie')

@register(Anecdote)
class AnecdoteTranslationOptions(TranslationOptions):
    fields = ('contenu',)