"""
Structure du Projet FastAPI
============================

projet_backend/
│
├── main.py                      # Point d'entrée de l'application
├── requirements.txt             # Dépendances
│
├── config/
│   └── database.py             # Configuration base de données
│
├── models/
│   ├── __init__.py
│   ├── schemas.py              # Schémas Pydantic
│   └── responses.py            # Modèles de réponse
│
├── services/
│   ├── __init__.py
│   ├── excel_service.py        # Service d'import Excel
│   ├── statistics_service.py  # Service de statistiques
│   └── auth_service.py         # Service d'authentification
│
├── routes/
│   ├── __init__.py
│   ├── upload.py               # Routes upload
│   ├── statistics.py           # Routes statistiques
│   ├── materiels.py            # Routes matériels
│   └── auth.py                 # Routes authentification
│
└── utils/
    ├── __init__.py
    ├── security.py             # Utilitaires sécurité
    └── helpers.py              # Fonctions utilitaires

Installation:
-------------
pip install fastapi uvicorn mysql-connector-python pandas openpyxl python-multipart passlib[bcrypt] python-jose[cryptography]

Lancement:
----------
uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""