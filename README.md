# API Gestion d'Écoles & E-Learning — Projet G6

Backend **Django + Django REST Framework** pour l'application « Gestion d'Écoles & E-Learning Mobile ».
Une seule base de code, découpée en 5 apps qui correspondent aux 5 services demandés :

| Service demandé       | App Django   | Préfixe API                |
|-----------------------|--------------|----------------------------|
| Auth-Service          | `accounts`   | `/api/v1/auth/`, `/api/v1/users/` |
| Academic-Service      | `academic`   | `/api/v1/academic/`        |
| Media-Service         | `mediahub`   | `/api/v1/media/`           |
| Billing-Service       | `billing`    | `/api/v1/billing/`         |
| Assessment-Service    | `assessment` | `/api/v1/assessment/`      |

Documentation interactive (pour l'équipe Flutter) : **`/api/docs/`** (Swagger) · `/api/redoc/` · schéma OpenAPI : `/api/schema/`

## Installation

```bash
python -m venv venv && venv\Scripts\activate        # Windows  (Linux/Mac : source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env                                # Linux/Mac : cp .env.example .env
python manage.py migrate
python manage.py seed_demo                            # comptes + données de démonstration
python manage.py runserver 0.0.0.0:8000               # 0.0.0.0 pour que l'équipe mobile y accède sur le réseau local
```

Comptes de démo (mot de passe `Demo12345!`) : `admin`, `teacher1`, `student1`, `student2`.

**MariaDB** : décommenter `mysqlclient` dans `requirements.txt`, créer la base (`utf8mb4`), puis renseigner `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` dans `.env`. Sans `DB_NAME`, SQLite est utilisé.

**Tests** : `python manage.py test tests`

## Authentification (JWT)

1. `POST /api/v1/auth/login/` `{ "username", "password" }` → `{ access, refresh, user }`
2. Chaque requête : en-tête `Authorization: Bearer <access>`
3. `POST /api/v1/auth/refresh/` `{ "refresh" }` → nouveau `access` (le refresh tourne : stocker le nouveau)
4. `POST /api/v1/auth/logout/` `{ "refresh" }` invalide le refresh token

Rôles (`user.role`) : `student`, `teacher`, `admin`. L'inscription publique (`/auth/register/`) crée toujours un **étudiant** ; l'admin crée les enseignants via `/users/`.

Listes paginées : `{ count, next, previous, results }` (`?page=`, `?page_size=`), avec `?search=`, `?ordering=` et des filtres par champ (voir Swagger).

## Endpoints par fonctionnalité du cahier des charges

### Étudiant
| Besoin | Endpoint |
|---|---|
| Liste des cours / s'inscrire | `GET /academic/courses/` · `POST /academic/courses/{id}/enroll/` · `GET /academic/courses/mine/` |
| Emploi du temps | `GET /academic/timetable/` (déjà filtré sur ses cours) |
| Suivi des cours (vidéos/documents) | `GET /media/materials/?course={id}` · `GET /media/materials/{id}/stream/` · `.../download/` · `POST /media/materials/{id}/progress/` `{completed, last_position_seconds}` · `GET /media/courses/{id}/progress/` |
| Payer scolarité / module (Mobile Money) | `POST /billing/payments/` `{installment` **ou** `course, provider, phone_number}` · `GET /billing/my-account/` · `GET /billing/payments/{id}/` (polling du statut) |
| Quiz / devoirs | `GET /assessment/quizzes/` · `POST /assessment/quizzes/{id}/start/` · `POST /assessment/attempts/{id}/submit/` · `GET /assessment/attempts/{id}/` (résultat) |
| Relevé de notes | `GET /academic/transcript/` |

### Enseignant / Admin
| Besoin | Endpoint |
|---|---|
| Gérer ses cours, emploi du temps | `POST/PATCH/DELETE /academic/courses/`, `/academic/timetable/` |
| Dépôt de supports de cours | `POST /media/materials/` (**multipart** : `course, title, kind, file`) |
| Création de devoirs/quiz | `POST /assessment/quizzes/` puis `POST /assessment/questions/` (avec `choices` imbriqués) |
| Correction manuelle (réponses libres) | `POST /assessment/attempts/{id}/grade/` |
| Saisie des notes | `POST /academic/grades/` ou en lot `POST /academic/grades/bulk/` |
| Suivi du règlement des frais | `GET /billing/tracking/?course=&status=paid\|partial\|unpaid` |
| Admin : frais, tranches, utilisateurs | `/billing/fees/`, `/billing/installments/`, `/users/`, `POST /billing/payments/{id}/confirm/` |

## Points d'intégration importants pour Flutter

- **Streaming vidéo** : `GET /media/materials/{id}/stream/` supporte l'en-tête HTTP `Range` (réponse `206`), donc lecture progressive et déplacement dans la vidéo. Le lecteur doit envoyer l'en-tête `Authorization` (ex. `VideoPlayerController.networkUrl(..., httpHeaders: {...})`). Les fichiers ne sont **jamais** exposés par une URL publique.
- **Accès aux contenus** : un étudiant voit les supports/quiz d'un cours seulement s'il est inscrit **et**, si le cours est payant (`price > 0`), après paiement réussi. Un support marqué `is_free_preview` reste visible.
- **Paiement Mobile Money** : le `POST /billing/payments/` renvoie `status: "pending"` + `message` ; l'app interroge ensuite `GET /billing/payments/{id}/` jusqu'à `success` ou `failed`. Le numéro est normalisé en `+257XXXXXXXX`. Fournisseurs : `lumicash`, `ecocash`, `other`.
- **Quiz** : `start` ne renvoie jamais les bonnes réponses. QCM corrigés automatiquement à la soumission ; réponses libres (`type: "text"`) en attente de l'enseignant (`status: "submitted"`, puis `"graded"`). La note finale est reportée automatiquement dans le relevé de notes (`counts_for_grade`). Une tentative a une durée limite (`duration_minutes`) avec 2 minutes de tolérance réseau.
- **Erreurs** : `400` avec le détail des champs, `401` token absent/expiré (rafraîchir), `403` rôle insuffisant, `404` ressource inexistante *ou non accessible*.

## Limites connues (à connaître avant la démo)

- **Mobile Money** : la passerelle fournie est **simulée** (`MOBILE_MONEY_AUTO_CONFIRM=True` confirme tout de suite ; `False` laisse le paiement en attente jusqu'au webhook `POST /billing/webhook/`, signé HMAC-SHA256 dans `X-Signature`, ou jusqu'à `confirm/` par l'admin). Brancher un vrai opérateur = ajouter une classe dans `billing/gateways.py`.
- **Streaming « adaptatif »** : implémenté en streaming progressif par plages (Range). Un vrai streaming à débit adaptatif (HLS, plusieurs qualités) demande un transcodage (ffmpeg) non inclus.
- Architecture : **monolithe modulaire** (5 apps découplées dans un seul projet) plutôt que 5 déploiements séparés ; chaque app peut être extraite en service autonome plus tard.
