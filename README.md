## NumerizeMe

NumerizeMe est une application de matching basee sur des questionnaires binaires.
Le projet est compose de:
- un backend FastAPI + SQLAlchemy + PostgreSQL
- un frontend Flutter (Android/iOS/Web/Desktop scaffold)

Ce README documente en detail:
1. le fonctionnement exact de l application actuelle
2. la procedure de lancement local
3. l etat de scalabilite
4. une strategie de deploiement serveur
5. ce qui manque pour une future commercialisation

## 1) Vision Produit Et Flux Fonctionnel

Le parcours utilisateur principal implemente aujourd hui est:
1. inscription (`POST /api/register`) ou connexion (`POST /api/login`)
2. stockage du token JWT dans le frontend
3. consultation de la liste des questionnaires
4. reponse a des questions binaires (A/B)
5. sauvegarde des reponses en base
6. calcul des compatibilites entre utilisateurs (indice de Jaccard)
7. affichage des matchs

Une couche de conversation est presente dans le code (endpoints + ecran Flutter), mais elle depend d une table `messages` qui n est pas active dans les modeles/migrations actuels (details plus bas).

## 2) Architecture Technique

### 2.1 Vue D Ensemble

- Frontend: `frontend/numerize_me_app`
- Backend: `backend`
- Orchestration locale: `docker-compose.yml`
- Base de donnees: PostgreSQL 13

Communication:
- Le frontend appelle le backend en HTTP REST
- URL API utilisee par Flutter: `http://10.0.2.2:8000/api` (emulateur Android)

### 2.1.1 Schema Mermaid Des Flux API/Frontend

```mermaid
flowchart TD
	A[Flutter App\nSplash/Login/Home] -->|POST /api/register\nPOST /api/login| B[FastAPI Router Auth]
	A -->|GET /api/users/me\nPUT /api/users/me| C[FastAPI Router Users]
	A -->|GET /api/questionnaires/questionnaires\nGET /api/questionnaires/responses/me\nPOST /api/questionnaires/responses| D[FastAPI Router Questionnaires]
	A -->|POST /api/matches/calculate-matches\nGET /api/matches/list-matches\nGET /api/matches/stats| E[FastAPI Router Matches]
	A -.->|GET/POST conversation endpoints| F[FastAPI Conversation Endpoints\n(messages table requise)]

	B --> G[Services + Security\nJWT + bcrypt]
	C --> H[User Service]
	D --> I[Questionnaire Service\n+ MatchingService trigger]
	E --> J[MatchingService\nJaccard similarity]
	F -.-> K[(Table messages)]

	G --> L[(PostgreSQL)]
	H --> L
	I --> L
	J --> L

	L --> M[Tables actives\nusers\nquestionnaires\nuser_responses\nmatches]
	K -.-> N[Etat actuel:\nmodele Message commente\nrisque erreur runtime]
```

### 2.2 Backend - Structure Et Responsabilites

#### Point d entree

Fichier: `backend/app/main.py`

Comportements au demarrage:
- creation automatique des tables SQLAlchemy (`Base.metadata.create_all`)
- execution de `init_questionnaires(db)` via startup event

Important:
- `init_questionnaires` est vide dans `backend/app/db/init_db.py`
- les questionnaires ne sont donc pas seeds automatiquement
- il faut injecter les donnees via scripts SQL

Middlewares:
- CORS ouvert (`allow_origins=["*"]`) pour le dev

Routes montees reellement dans l application:
- `auth.router` sur prefix `/api`
- `users.router` sur prefix `/api/users`
- `questionnaires.router` sur prefix `/api/questionnaires`
- `matches.router` sur prefix `/api/matches`
- `test.router` sur prefix `/api/test`

Routes non montees:
- `backend/app/api/social.py`
- `backend/app/api/matches_temp.py`

#### Config Et securite

Fichiers:
- `backend/app/core/config.py`
- `backend/app/core/security.py`

Points cles:
- JWT HS256
- `SECRET_KEY` en valeur par defaut dans le code (a externaliser en prod)
- mot de passe hash avec bcrypt (`passlib`)
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")`

#### Couche base de donnees

Fichier: `backend/app/db/base.py`

- `DATABASE_URL` lue depuis settings
- `engine` SQLAlchemy + `SessionLocal`
- dependance FastAPI `get_db()`

#### Modeles SQLAlchemy

Fichiers:
- `backend/app/models/user.py`
- `backend/app/models/questionnaire.py`
- `backend/app/models/match.py`
- `backend/app/models/social.py`

Tables actives:
- `users`
- `questionnaires`
- `user_responses`
- `matches`

Tables/couches non finalisees:
- `messages` est commentee dans `match.py`
- `social.py` contient une table d association `user_matches` non branchee dans le flux principal

#### Schemas Pydantic

Fichiers:
- `backend/app/schemas/user.py`
- `backend/app/schemas/questionnaire.py`
- `backend/app/schemas/match.py`
- `backend/app/schemas/social.py`

Usage:
- validation des payloads d entree (`UserCreate`, `UserLogin`, `UserResponseCreate`)
- serialisation des reponses API (`UserProfile`, `MatchResponse`, etc.)

#### Services metier

Fichiers:
- `backend/app/services/user_service.py`
- `backend/app/services/questionnaire_service.py`
- `backend/app/services/matching_service.py`
- `backend/app/services/temp_questionnaire_service.py`

Logique de matching:
- construction d ensembles de tuples `(questionnaire_id, question_id, chosen_option)`
- calcul de similarite Jaccard:

$$
similarite = \frac{|A \cap B|}{|A \cup B|}
$$

- seuil minimum applique dans `find_matches_for_user`: `0.3`
- creation ou mise a jour d un enregistrement `matches` par paire d utilisateurs

#### API exposee (effective)

Authentification:
- `POST /api/register`
- `POST /api/login`

Utilisateur:
- `GET /api/users/me`
- `PUT /api/users/me`
- `POST /api/users/me/picture`

Questionnaires:
- `GET /api/questionnaires/test`
- `GET /api/questionnaires/questionnaires-test`
- `GET /api/questionnaires/test-completion`
- `GET /api/questionnaires/questionnaires`
- `GET /api/questionnaires/questionnaires/{questionnaire_id}`
- `POST /api/questionnaires/responses`
- `GET /api/questionnaires/responses/me`

Matching:
- `GET /api/matches/test-simple`
- `GET /api/matches/list-matches`
- `GET /api/matches/stats`
- `GET /api/matches/test-db`
- `POST /api/matches/calculate-matches`
- `POST /api/matches/recalculate-all-matches`
- `POST /api/matches/conversation/{match_id}/message`
- `GET /api/matches/conversation/{match_id}`
- `POST /api/matches/conversation/{match_id}/mark-read`

Test:
- `POST /api/test/test-matching`

#### Attention sur la conversation

Les endpoints conversation utilisent SQL brut sur table `messages`.
Or la classe `Message` est commentee dans `backend/app/models/match.py`.
Conclusion:
- API conversation presente dans le code
- mais risque d erreur runtime tant que la table `messages` n existe pas

#### Migrations Alembic

Fichiers:
- `backend/alembic/versions/001_add_user_profile_fields.py`
- `backend/alembic/env.py`

Point critique:
- `env.py` importe `Message` depuis `app.models.match`
- cette classe est commentee actuellement
- `alembic upgrade head` peut donc echouer sans correction prealable

### 2.3 Frontend Flutter - Structure Et Flux

Point d entree:
- `frontend/numerize_me_app/lib/main.dart`

State management:
- `AuthProvider`
- `QuestionnaireProvider`
- `ProfileProvider`

Ecran initial:
- `SplashScreen`
- verifie le token persiste (`SharedPreferences`)
- redirige vers login ou home

Navigation principale:
- `SimpleHomeScreen` + `BottomNavigationBar` a 4 onglets
1. accueil
2. questionnaires
3. matchs
4. profil

Services reseau:
- `auth_service.dart`
- `questionnaire_service.dart`
- `match_service.dart`
- `profile_service.dart`

Configuration API:
- `frontend/numerize_me_app/lib/core/api_config.dart`
- `baseUrl = http://10.0.2.2:8000/api`

Details fonctionnels:
- Auth:
	- login/inscription via backend
	- token stocke en clair dans `SharedPreferences`
- Questionnaires:
	- charge la liste des questionnaires
	- charge les reponses utilisateur pour marquer `isCompleted`
	- envoi des reponses avec `question_id` + `chosen_option`
- Matchs:
	- l ecran lance d abord `calculate-matches`
	- puis recupere `list-matches`
- Profil:
	- lecture/modification de `first_name`, `last_name`, `age`, `city`, `bio`
- Conversation:
	- UI implementee
	- depend des endpoints/messages cote backend

## 3) Fonctionnement Des Donnees (Exact)

### 3.1 Questionnaires

Les questionnaires sont stockes en JSON dans la colonne `questionnaires.questions`.

Format attendu par le frontend actuel:
```json
{
	"id": 1,
	"text": "...",
	"option_a": "...",
	"option_b": "..."
}
```

### 3.2 Reponses utilisateur

Payload envoye par Flutter:
```json
{
	"questionnaire_id": 1,
	"answers": [
		{"question_id": 1, "chosen_option": "A"},
		{"question_id": 2, "chosen_option": "B"}
	]
}
```

### 3.3 Impact direct sur le matching

Apres creation/mise a jour d une reponse:
- l endpoint `POST /api/questionnaires/responses` tente de recalculer les matchs
- `MatchingService.find_matches_for_user` compare l utilisateur courant avec les autres
- `create_or_update_match` persiste le score

## 4) Lancer Le Projet En Local

## 4.1 Prerequis

- Docker Desktop (pour mode Docker)
- OU Python 3.9 + PostgreSQL 13 (pour mode manuel backend)
- Flutter SDK (pour frontend)
- Android Studio (si test emulateur Android)

## 4.2 Mode Docker (backend + db)

Depuis la racine du projet:

```bash
docker compose up --build
```

Services disponibles:
- API FastAPI: `http://localhost:8000`
- Docs Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Postgres: `localhost:5432`

Important: les questionnaires ne sont pas auto-seedes.
Il faut injecter un script SQL compatible.

### Script recommande

Utiliser en priorite:
- `backend/insert_questionnaires_utf8.sql`
ou
- `backend/insert_questionnaires_binary.sql`

Ces scripts utilisent les cles JSON attendues (`id`, `text`, `option_a`, `option_b`).

Exemple d import SQL dans le conteneur db:

```bash
docker exec -i numerizeme-db-1 psql -U postgres -d numerize_me < backend/insert_questionnaires_utf8.sql
```

Note:
- le nom de conteneur peut differer selon votre machine (`docker ps`)

## 4.3 Mode Manuel Backend (sans Docker)

### Etapes

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Creer `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/numerize_me
SECRET_KEY=change-me-in-local
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Creer la base:

```bash
createdb -U postgres numerize_me
```

Lancer l API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Seeder les questionnaires (depuis un autre terminal):

```bash
psql -U postgres -d numerize_me -f insert_questionnaires_utf8.sql
```

## 4.4 Lancer Le Frontend Flutter

```bash
cd frontend/numerize_me_app
flutter pub get
flutter run
```

Pour emulateur Android:
- garder `10.0.2.2` dans `api_config.dart`

Pour telephone physique:
- remplacer l URL API par l IP locale du PC
- exemple: `http://192.168.1.20:8000/api`

## 4.5 Verification Rapide

1. Ouvrir `http://localhost:8000/health` -> `{"status":"ok"}`
2. Ouvrir `http://localhost:8000/docs`
3. Dans Flutter:
	- creer un compte
	- repondre a au moins un questionnaire
	- aller dans l onglet matchs

## 5) Incoherences Et Points A Connaitre Avant Debug

1. `backend/insert_questionnaires.sql` n utilise pas le meme schema JSON que le frontend.
2. `backend/insert_questionnaires_fixed.sql` utilise `options` au lieu de `option_a/option_b`.
3. `backend/insert_test_users.sql` stocke des reponses avec cle `choice` au lieu de `chosen_option` et cible des IDs de questionnaires eleves (ex: 13, 14), ce qui peut etre incompatible selon l etat de la base.
4. Endpoints conversation dependants d une table `messages` non active.
5. Alembic peut etre casse a cause d un import `Message` non resolu dans `backend/alembic/env.py`.

## 6) Scalabilite: Etat Actuel

Reponse courte: le projet est un bon prototype technique, mais pas encore scalable tel quel pour une forte charge production.

### 6.1 Ce qui scale deja correctement

- separation frontend/backend
- backend stateless cote API (JWT)
- base relationnelle solide (PostgreSQL)
- logique metier decoupee dans des services

### 6.2 Limites actuelles

1. CORS totalement ouvert.
2. secret JWT en dur par defaut.
3. pas de rate limiting.
4. pas de cache (questionnaires, stats, matching).
5. matching potentiellement couteux quand le nombre d utilisateurs augmente.
6. JSON en colonnes pour questions/reponses (pratique, mais limite pour indexation analytique fine).
7. logs debug/print abondants en production path.
8. pas de monitoring/alerting.
9. couche conversation incomplete.

## 7) Comment Deployer Sur Un Serveur

Ci dessous, une trajectoire simple et robuste pour un deploiement realiste.

### 7.1 Cible recommandee (MVP pro)

- 1 VM Linux (ou 2):
	- Nginx (reverse proxy + TLS)
	- backend FastAPI en conteneur
	- PostgreSQL gere (ou conteneur dedie)
	- Redis (cache + jobs)

### 7.2 Etapes techniques

1. Containeriser proprement backend (deja fait) sans `--reload` en prod.
2. Ajouter serveur ASGI prod (`gunicorn` + workers uvicorn).
3. Injecter secrets via variables d environnement (jamais en dur).
4. Restreindre CORS aux domaines frontend.
5. Activer TLS (Lets Encrypt via Nginx/Caddy).
6. Mettre en place migrations fiables (corriger Alembic/env.py).
7. Ajouter pipeline CI/CD:
	 - tests
	 - build image
	 - push registry
	 - deploy automatise
8. Ajouter sauvegardes automatiques PostgreSQL + strategie de restore.
9. Ajouter observabilite:
	 - logs structures
	 - metrics Prometheus/Grafana
	 - traces APM

### 7.3 Deployment frontend Flutter

Options:
1. Mobile natif: build APK/AAB (Android) et IPA (iOS).
2. Web Flutter: servir build statique derriere Nginx/CDN.

A prevoir:
- gestion d environnements (`dev`, `staging`, `prod`)
- URL API par environnement
- gestion des certificats et pinning si necessaire

## 8) Ce Qui Manque Pour Une Commercialisation

Pour passer de prototype a produit commercialisable, il manque principalement:

### 8.1 Produit

1. fiabiliser completement la messagerie
2. definir les regles de matching business (pas seulement Jaccard brut)
3. ajouter filtres/recherche/preferences avancees
4. UX polishing + accessibilite + internationalisation

### 8.2 Technique

1. batterie de tests (unitaires, integration, e2e)
2. correction des incoherences schema SQL/scripts
3. migration DB propre et reproductible
4. securisation du stockage token (ex: secure storage mobile)
5. architecture de cache et jobs asynchrones

### 8.3 Securite Et conformite

1. durcissement auth (refresh token, revocation, rotation)
2. protections abuse (rate limit, anti brute force)
3. validation stricte des uploads image
4. chiffrement transit + bonnes pratiques secret management
5. conformite RGPD (consentement, droit a l oubli, export data)

### 8.4 Operations

1. CI/CD complet + environnements de staging
2. runbooks incident + alerting
3. SLA/SLO et monitoring des temps de reponse
4. plan de reprise et sauvegardes testees

## 9) Plan D Action Prioritaire (Pragmatique)

Sprint 1 (stabilisation):
1. corriger script seed unique et compatible frontend
2. corriger/retirer endpoints conversation tant que `messages` n est pas migree
3. corriger Alembic pour migrations fiables
4. externaliser `SECRET_KEY` et fermer CORS

Sprint 2 (production readiness):
1. ajouter tests API critiques
2. ajouter rate limiting + logs structures
3. mettre en place CI/CD + deploiement staging
4. configurer monitoring/alerting minimal

Sprint 3 (scalabilite):
1. ajouter cache Redis
2. deplacer calculs lourds en jobs asynchrones
3. optimiser modele de donnees reponses/questionnaires selon besoins analytiques

## 10) Commandes Utiles

### Docker

```bash
docker compose up --build
docker compose down
docker compose ps
docker logs -f <backend_container>
docker logs -f <db_container>
```

### Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend/numerize_me_app
flutter pub get
flutter run
```
