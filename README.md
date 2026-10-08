# E-Learning — Gestion d'Écoles (Django REST + MariaDB)

Rôles : **Étudiant**, **Enseignant**, **Back office** · Streaming vidéo/documents · Quiz interactifs · Paiement des frais.

## Lancer (MariaDB)
```bash
python -m venv venv && source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # adapter DB_USER / DB_PASSWORD
# MariaDB : CREATE DATABASE elearning_db CHARACTER SET utf8mb4;
python manage.py migrate
python manage.py seed_demo                           # comptes + données de démonstration
python manage.py runserver
```
Test rapide sans MariaDB : mettre `USE_SQLITE=True` dans `.env`.

## Accès
- Application web : http://127.0.0.1:8000/
- Swagger (pour Flutter) : http://127.0.0.1:8000/api/docs/
- Back office Django : http://127.0.0.1:8000/admin/
- Comptes démo : `admin/admin12345` · `prof/prof12345` · `etudiant/etud12345`

## API (JWT : `Authorization: Bearer <access>`)
`POST /api/auth/login/` · `/auth/refresh/` · `/auth/register/` · `GET /auth/me/`
`/api/courses/` · `/api/lessons/?course=` · `GET /api/lessons/{id}/stream/` (Range, `?token=` pour `<video>`)
`/api/quizzes/` · `POST /api/quizzes/{id}/attempt/` · `/api/attempts/`
`/api/fees/` · `POST /api/payments/` · `GET /api/payments/{id}/receipt/` · `/api/stats/` (admin)
`/api/schools/` · `/api/classrooms/` · `/api/enrollments/` · `/api/users/` (admin)

Paiement : `payments/gateway.py` est une **simulation** ; y brancher le vrai fournisseur.
Tests : `python manage.py test`
