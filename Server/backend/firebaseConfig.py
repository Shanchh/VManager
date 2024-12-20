import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("config/firebase_config.json")

firebase_admin.initialize_app(cred)

db = firestore.client()

__all__ = ["db", "auth"]