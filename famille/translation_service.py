from deep_translator import GoogleTranslator

def traduire_texte(texte, langue_cible='fr', langue_origine='auto'):
    if not texte:
        return ""

    try:
        # Traduction réelle avec Google Translate
        traduction = GoogleTranslator(source=langue_origine, target=langue_cible).translate(texte)
        return traduction
    except Exception as e:
        # En cas d'erreur réseau, on retourne le texte original
        return texte