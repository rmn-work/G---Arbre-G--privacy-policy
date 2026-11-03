import firebase_admin
from firebase_admin import credentials, messaging

# Chemin vers votre fichier JSON téléchargé
cred = credentials.Certificate("votre-fichier-de-cle-secrete.json")
firebase_admin.initialize_app(cred)

def envoyer_notification(token_appareil, titre, corps):
    message = messaging.Message(
        notification=messaging.Notification(title=titre, body=corps),
        token=token_appareil,
    )
    # Envoi du message via Firebase
    response = messaging.send(message)
    return response