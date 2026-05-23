# Документация: ApartmentForRent - Платформа прогнозирования цен на аренду

## Оглавление
1. [Архитектура](#архитектура)
2. [Стек технологий](#стек-технологий)
3. [Структура проекта](#структура-проекта)
4. [Запуск приложения](#запуск-приложения)
5. [Backend API](#backend-api)
6. [Frontend](#frontend)
7. [ML Model Integration](#ml-model-integration)
8. [Docker & Infrastructure](#docker--infrastructure)
9. [Troubleshooting](#troubleshooting)
10. [Deployment](#deployment)

---

## Архитектура

### Общая структура
```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │         Nginx (Port 80)           │
            │  - Reverse Proxy                  │
            │  - Static files serving           │
            │  - API routing (/api/...)         │
            └──────────────────────────────────┘
                     │                  │
         ┌───────────┘                  └──────────────┐
         │                                             │
         ▼                                             ▼
   ┌──────────────┐                          ┌──────────────────┐
   │ Frontend:3000│                          │  Backend:8000    │
   │ Next.js/React│                          │ FastAPI/Uvicorn  │
   │              │                          │                  │
   │ - Auth pages │                          │ - Auth API       │
   │ - Dashboard  │                          │ - Predictions API│
   │ - Analytics  │                          │ - ML Inference   │
   └──────────────┘                          └──────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────┐
                       │                              │                          │
                       ▼                              ▼                          ▼
              ┌──────────────────┐        ┌──────────────────┐      ┌──────────────────┐
              │  PostgreSQL:5432 │        │  Redis:6379      │      │  RabbitMQ:5672   │
              │  Database        │        │  Cache & Sessions│      │  Message Broker  │
              │  - Users         │        │  - Auth tokens   │      │  - Celery tasks  │
              │  - Predictions   │        │  - Predictions   │      │  - Async jobs    │
              │  - Images        │        │    cache         │      │                  │
              │  - Logs          │        │                  │      │                  │
              └──────────────────┘        └──────────────────┘      └──────────────────┘
                       │
                       ▼
              ┌──────────────────────┐
              │   ML Model           │
              │   CatBoostRegressor  │
              │   - 76 features      │
              │   - RMSE loss        │
              │   - 2000 iterations  │
              └──────────────────────┘
```

### Поток данных для прогнозирования

```
Frontend (Dashboard)
        │
        │ POST /api/predictions
        │ {title, region, city, metro, square, rooms_clean, 
        │  floor, max_floor, time_to_metro, description, ...}
        ▼
API Gateway (Nginx)
        │
        │ /api/ → /
        ▼
Backend (FastAPI)
        │
        ├─ 1. Validate Input
        │      └─ Check required fields
        │
        ├─ 2. Feature Preprocessing
        │      ├─ Numerical features: square, floor, rooms, etc.
        │      ├─ Derived features: floor_ratio, log_square, etc.
        │      ├─ Categorical encoding: region, city, metro (TargetEncoder)
        │      ├─ Text processing: description → TF-IDF (30 features)
        │      ├─ One-hot encoding: floor_category, building_height, etc.
        │      └─ Result: 76-feature vector
        │
        ├─ 3. ML Inference
        │      └─ model.predict([76 features]) → price
        │
        ├─ 4. Store in PostgreSQL
        │      └─ Save: prediction, features, timestamp
        │
        └─ 5. Return Response
               └─ {id, predicted_price, confidence_score, ...}
              
Frontend
        │
        └─ Display: "Price: ₽50,000/month"
```

---

## Стек технологий

### Backend
- **FastAPI 0.104.1** - async web framework
- **Uvicorn 0.24.0** - ASGI server
- **SQLAlchemy 2.0.23** - ORM
- **AsyncPG 0.29.0** - async PostgreSQL driver
- **Pydantic 2.5.3** - data validation
- **CatBoost 1.2.5** - gradient boosting ML model
- **scikit-learn 1.3.2** - feature preprocessing (TF-IDF, TargetEncoder)
- **Celery 5.3.4** - async task queue
- **Redis 5.0.1** - cache & message broker

### Frontend
- **Next.js 15** - React framework
- **React 18.2** - UI library
- **TypeScript 5.6** - type safety
- **Axios 1.6** - HTTP client
- **TailwindCSS 3.4** - styling
- **Zustand 4.4** - state management
- **React Hot Toast 2.4** - notifications

### Infrastructure
- **PostgreSQL 16** - relational database
- **Redis 7** - in-memory cache
- **RabbitMQ 3.13** - message broker
- **Nginx** - reverse proxy
- **Docker & Docker Compose** - containerization
- **Prometheus & Grafana** - monitoring

---

## Структура проекта

```
ApartmentForRent/
├── backend/                      # FastAPI приложение
│   ├── app/
│   │   ├── __init__.py          # Main FastAPI app
│   │   ├── api/
│   │   │   ├── auth/            # Authentication endpoints
│   │   │   ├── predictions/     # Predictions endpoints
│   │   │   └── uploads/         # File upload endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Settings & environment
│   │   │   ├── security.py      # JWT, password hashing
│   │   │   ├── exceptions.py    # Custom exceptions
│   │   │   └── constants.py     # App constants
│   │   ├── ml/
│   │   │   └── model_loader.py  # ML model loading & preprocessing
│   │   ├── models/
│   │   │   ├── __init__.py      # SQLAlchemy ORM models
│   │   │   └── database.py      # Database config & session
│   │   ├── schemas/
│   │   │   └── __init__.py      # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── prediction_service.py  # Prediction business logic
│   │   │   ├── auth_service.py        # Auth business logic
│   │   │   ├── user_service.py        # User management
│   │   │   └── image_service.py       # Image processing
│   │   ├── repositories/
│   │   │   ├── base_repository.py     # Base CRUD operations
│   │   │   ├── prediction_repository.py
│   │   │   └── user_repository.py
│   │   ├── utils/
│   │   │   ├── logger.py        # Logging setup
│   │   │   ├── validators.py    # Custom validators
│   │   │   └── auth_decorator.py # Auth dependency
│   │   ├── workers/
│   │   │   └── celery_app.py    # Async task queue
│   │   └── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── migrations/              # Alembic DB migrations
│
├── frontend/                     # Next.js приложение
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Home page
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── auth/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── dashboard/page.tsx    # Main dashboard
│   │   │   └── analytics/page.tsx    # Analytics page
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   └── ImageUpload.tsx
│   │   ├── services/
│   │   │   └── api.ts           # API client & methods
│   │   ├── store/
│   │   │   └── auth.ts          # Zustand auth store
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript interfaces
│   │   ├── utils/
│   │   │   └── helpers.ts       # Utility functions
│   │   └── hooks/               # Custom React hooks
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── Dockerfile
│   └── .env                     # Environment variables
│
├── nginx/
│   └── nginx.conf               # Nginx reverse proxy config
│
├── prometheus/
│   └── prometheus.yml           # Prometheus config
│
├── docker-compose.yml           # Container orchestration
├── rental_price_model.pkl       # Trained ML model
├── .env                         # Root environment variables
├── .env.example                 # Environment template
├── start.sh                     # Startup script
└── README.md
```

---

## Запуск приложения

### 1. Требования

- Docker & Docker Compose
- OR: Python 3.12+, Node.js 20+, PostgreSQL 16, Redis 7

### 2. Локальный запуск (без Docker)

#### Подготовка

```bash
# Установить Python зависимости
pip install -r backend/requirements.txt

# Установить Node.js зависимости
cd frontend
npm install
cd ..
```

#### Запуск Backend

```bash
# Из корня проекта
cd backend

# Экспортировать путь модели
export MODEL_PATH=../rental_price_model.pkl
export DATABASE_URL=postgresql://apartment_user:password@localhost:5432/apartment_rent
export DEBUG=False

# Запустить
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Backend будет доступен на: http://localhost:8000
Swagger docs: http://localhost:8000/docs

#### Запуск Frontend

```bash
# Из frontend директории
export NEXT_PUBLIC_API_URL=http://localhost:8000/api

npm run dev
```

Frontend будет доступен на: http://localhost:3000

### 3. Docker-Compose запуск (РЕКОМЕНДУЕТСЯ)

```bash
# Из корня проекта

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотреть логи
docker-compose logs -f backend
docker-compose logs -f frontend

# Остановить
docker-compose down
```

**Сервисы будут доступны на:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Nginx reverse proxy: http://localhost
- API docs: http://localhost/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:8080 (admin/admin123)

---

## Backend API

### Authentication Endpoints

#### POST /auth/register
Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLC...",
  "token_type": "bearer"
}
```

#### POST /auth/login
Вход пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** (same as register)

#### POST /auth/refresh
Обновление access токена.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLC..."
}
```

**Response:** (same as login)

### Prediction Endpoints

#### POST /predictions
Создание нового прогноза с ML inference.

**Request:**
```json
{
  "title": "Apartment in Moscow",
  "description": "Nice 2-room apartment with furniture",
  "region": "Moscow",
  "city": "Moscow",
  "metro": "Red Square",
  "street_type": "улица",
  "square": 50,
  "rooms_clean": 2,
  "floor": 2,
  "max_floor": 5,
  "time_to_metro": 10,
  "has_furniture": true,
  "has_appliances": true,
  "has_wifi": true,
  "renovation_euro": true,
  "pets_allowed": false,
  "children_allowed": true,
  "floor_category": "middle",
  "building_height": "mid_rise",
  "size_category": "medium",
  "metro_accessibility": "close"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Apartment in Moscow",
  "predicted_price": 50000.50,
  "confidence_score": null,
  "square": 50,
  "rooms_clean": 2,
  "floor": 2,
  "max_floor": 5,
  "region": "Moscow",
  "city": "Moscow",
  "metro": "Red Square",
  "created_at": "2026-05-21T15:00:00Z",
  "updated_at": "2026-05-21T15:00:00Z",
  "images": []
}
```

#### GET /predictions
Получить список прогнозов пользователя.

**Query Parameters:**
- `skip`: int = 0
- `limit`: int = 20 (max 100)

**Response:**
```json
[
  { "id": 1, "title": "...", "predicted_price": 50000.50, ... },
  { "id": 2, "title": "...", "predicted_price": 45000.00, ... }
]
```

#### GET /predictions/{prediction_id}
Получить детали прогноза.

**Response:**
```json
{
  "id": 1,
  "title": "Apartment in Moscow",
  "predicted_price": 50000.50,
  "square": 50,
  "rooms_clean": 2,
  "images": [
    {
      "id": 1,
      "prediction_id": 1,
      "file_name": "photo_1.jpg",
      "file_size": 125456,
      "mime_type": "image/jpeg",
      "created_at": "2026-05-21T15:00:00Z"
    }
  ]
}
```

#### DELETE /predictions/{prediction_id}
Удалить прогноз (cascade delete для images).

**Response:** 204 No Content

#### GET /predictions/stats/analytics
Получить статистику прогнозов пользователя.

**Response:**
```json
{
  "total": 10,
  "avg_price": 48000,
  "min_price": 35000,
  "max_price": 65000,
  "median_price": 50000
}
```

### Health Check

#### GET /health
Проверка здоровья приложения.

**Response:**
```json
{
  "status": "healthy",
  "app": "ApartmentForRent",
  "version": "1.0.0"
}
```

#### GET /metrics
Prometheus метрики для мониторинга.

---

## Frontend

### Структура страниц

#### Главная страница (/)
- Информация о приложении
- Ссылки на Register/Login
- Link на Dashboard для авторизованных пользователей

#### Регистрация (/auth/register)
- Форма с email, password, full_name
- Password validation: min 8 chars
- Email validation
- Redirect на dashboard после успешной регистрации

#### Вход (/auth/login)
- Email и password input
- Remember me (optional)
- Redirect на dashboard после успешного входа

#### Dashboard (/dashboard)
**Главная страница приложения с двумя частями:**

1. **Форма создания прогноза**
   - Inputs для всех 27 параметров модели
   - Real-time validation
   - Submit кнопка
   - Loading state

2. **Таблица прогнозов**
   - Список всех прогнозов пользователя
   - Pagination (20 на странице)
   - View, Delete actions
   - Display: title, city, price, area

#### Аналитика (/analytics)
- Graph: распределение цен
- Statistics: avg, min, max, median
- Charts по регионам

### State Management (Zustand)

**Auth Store** (`src/store/auth.ts`)
```typescript
{
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  login: (credentials) => Promise<void>;
  register: (data) => Promise<void>;
  logout: () => void;
  setUser: (user) => void;
}
```

### API Integration

**API Client** (`src/services/api.ts`)
- Base URL: `${process.env.NEXT_PUBLIC_API_URL}/api`
- Auto token injection in Authorization header
- Auto token refresh on 401
- Global error handling with toast notifications

---

## ML Model Integration

### Model Architecture

**Type:** CatBoostRegressor (Gradient Boosting)

**Training Parameters:**
- Loss function: RMSE
- Iterations: 2000
- Learning rate: 0.03
- Tree depth: 8
- Random seed: 42
- Early stopping: 50 rounds

### Model Input

**76 features:** 

#### Numerical (5)
- `square`: Apartment area in m²
- `floor`: Current floor
- `max_floor`: Total floors
- `rooms_clean`: Number of rooms
- `time_to_metro`: Time to metro in minutes

#### Derived Numerical (4)
- `floor_ratio`: floor / max_floor
- `rooms_per_square`: rooms / square
- `square_x_rooms`: square * rooms (interaction)
- `log_square`: log(square + 1)

#### Categorical/Encoded (11)
- `region`: Target encoded
- `city`: Target encoded
- `metro`: Target encoded
- `street_type`: Target encoded
- `price_per_sqm_estimate`: Precomputed estimate

#### Boolean/Amenities (20)
- `is_first_floor`, `is_last_floor`
- `has_furniture`, `has_appliances`
- `has_tv`, `has_wifi`, `has_dishwasher`
- `has_washing_machine`, `has_parking`
- `has_balcony`, `has_security`
- `renovation_euro`, `renovation_cosmetic`, `renovation_new`
- `pets_allowed`, `children_allowed`
- `is_new_building`, `has_metro`, `is_central`

#### One-Hot Encoded Categories (16)
- Floor category (3): low, middle, high
- Building height (3): mid_rise, high_rise, skyscraper
- Size category (4): small, medium, large, huge
- Metro accessibility (3): close, medium, far

#### Text-Based TF-IDF Features (30)
- Extracted from apartment `description`
- Russian stopwords removed
- TfidfVectorizer with 30 features

### Preprocessing Pipeline

```python
# 1. Input validation
validate_required_fields()

# 2. Numerical features
square → floor_ratio, log_square, rooms_per_square, square_x_rooms

# 3. Categorical encoding (TargetEncoder)
region, city, metro, street_type → encoded values

# 4. Boolean features
Convert bool → int (0/1)

# 5. One-hot encoding
floor_category → [floor_category_low, floor_category_middle, floor_category_high]

# 6. Text processing
description → clean (remove stopwords) → TfidfVectorizer → 30 features

# 7. Concatenate all 76 features
→ Feature vector (1, 76)

# 8. Model inference
CatBoost.predict(vector) → price (float)
```

### Model Performance

**Validation Metrics:**
- **R² Score (log):** 0.85+
- **RMSE:** ~8,000 RUB
- **MAE:** ~6,000 RUB

**Output Range:** 50,000 - 500,000 RUB (typical rental prices)

---

## Docker & Infrastructure

### Docker Compose Services

#### postgres (PostgreSQL 16)
```yaml
- Container: apartment_postgres
- Port: 5432
- Volumes: postgres_data
- Healthcheck: pg_isready
- Wait condition: service_healthy
```

#### redis (Redis 7)
```yaml
- Container: apartment_redis
- Port: 6379
- Volumes: redis_data
- Healthcheck: redis-cli ping
- Wait condition: service_healthy
```

#### rabbitmq (RabbitMQ 3.13)
```yaml
- Container: apartment_rabbitmq
- Ports: 5672 (AMQP), 15672 (Management)
- Volumes: rabbitmq_data
- Healthcheck: rabbitmq-diagnostics ping
- Wait condition: service_healthy
```

#### backend (FastAPI)
```yaml
- Container: apartment_backend
- Port: 8000
- Depends on: postgres (healthy), redis (healthy), rabbitmq (healthy)
- Volumes: ./backend/app, ./rental_price_model.pkl, ./uploads
- Healthcheck: GET /health
- Command: uvicorn app:app --host 0.0.0.0 --port 8000
```

#### celery_worker (Celery)
```yaml
- Container: apartment_celery_worker
- Depends on: postgres, redis, rabbitmq
- Command: celery -A app.workers.celery_app worker --loglevel=info
```

#### frontend (Next.js)
```yaml
- Container: apartment_frontend
- Port: 3000
- Depends on: backend
- Volumes: ./frontend, /app/node_modules, /app/.next
- Environment: NEXT_PUBLIC_API_URL=http://localhost:8000
- Command: npm start
```

#### nginx (Nginx)
```yaml
- Container: apartment_nginx
- Port: 80, 443
- Volumes: ./nginx/nginx.conf, ./uploads
- Depends on: backend, frontend
- Healthcheck: wget --quiet http://localhost/health
```

#### prometheus
```yaml
- Container: apartment_prometheus
- Port: 9090
- Volumes: ./prometheus/prometheus.yml, prometheus_data
- Storage retention: 15d
```

#### grafana
```yaml
- Container: apartment_grafana
- Port: 8080 (mapped from 3000)
- Depends on: prometheus
- Default credentials: admin / admin123
```

### Network

**Single bridge network:** `apartment_network`
- All services communicate via service names (DNS)
- Example: backend → `postgresql://apartment_user:password@postgres:5432/apartment_rent`

### Volumes

- **postgres_data**: PostgreSQL persistent data
- **redis_data**: Redis persistence
- **rabbitmq_data**: RabbitMQ persistence
- **prometheus_data**: Prometheus time-series data
- **./uploads**: Shared volume for uploaded images
- **./backend/app**: Backend code (hot reload)
- **./frontend**: Frontend code + node_modules

---

## Troubleshooting

### Backend не запускается

**Error: "Model not found at /app/rental_price_model.pkl"**

**Решение:**
- Убедитесь что `rental_price_model.pkl` находится в корне проекта
- В docker-compose проверьте volume mapping:
  ```yaml
  volumes:
    - ./rental_price_model.pkl:/app/rental_price_model.pkl
  ```
- Для локального запуска: `export MODEL_PATH=./rental_price_model.pkl`

**Error: "psycopg2.OperationalError: could not connect to server"**

**Решение:**
- Проверьте что PostgreSQL запущен: `docker-compose ps postgres`
- Проверьте connectionstring в `.env`
- Wait for healthcheck: `docker-compose logs postgres`

### Frontend не загружается

**Error: "Failed to load predictions"**

**Решение:**
- Check backend is running: `curl http://localhost:8000/health`
- Check CORS in backend config
- Check API URL in frontend: `echo $NEXT_PUBLIC_API_URL`
- Check nginx routing: `/api/` prefix stripping

**Error: "TypeError: Cannot read properties of undefined"**

**Решение:**
- API contract mismatch: check frontend types match backend schemas
- Check if user is authenticated: localStorage tokens
- Check browser console for detailed errors

### Prediction returns wrong price

**Error: "Prediction value seems unrealistic"**

**Решение:**
- Check all required fields are provided
- Check description is not empty (affects TF-IDF features)
- Verify categorical values are valid (region, city, metro, street_type)
- Check model features are 76 dimensional

### Database migration errors

**Error: "Alembic version ID is not set"**

**Решение:**
```bash
cd backend
alembic upgrade head
```

### Redis/RabbitMQ connection errors

**Error: "ConnectionRefusedError"**

**Решение:**
- Check services are running: `docker-compose ps`
- Check container logs: `docker-compose logs redis`
- Restart services: `docker-compose restart redis rabbitmq`

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Change all default passwords
- [ ] Generate new `SECRET_KEY` (min 32 chars)
- [ ] Configure CORS_ORIGINS for production domain
- [ ] Setup SSL/TLS certificates in nginx
- [ ] Enable database backups
- [ ] Configure monitoring alerts
- [ ] Test disaster recovery procedure
- [ ] Setup log aggregation (ELK, Datadog, etc.)
- [ ] Load testing

### Environment Variables (Production)

```env
APP_NAME=ApartmentForRent
DEBUG=False
VERSION=1.0.0

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql://user:securepass@db.prod.com:5432/apartment_rent
REDIS_URL=redis://redis.prod.com:6379/0
CELERY_BROKER_URL=amqp://guest:securepass@rabbitmq.prod.com:5672//

SECRET_KEY=generate-64-char-random-secure-key-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

LOG_LEVEL=INFO

# SSL
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Docker Registry Deployment

```bash
# Build images
docker-compose build

# Tag for registry
docker tag apartment_backend:latest registry.example.com/apartment_backend:1.0.0
docker tag apartment_frontend:latest registry.example.com/apartment_frontend:1.0.0

# Push to registry
docker push registry.example.com/apartment_backend:1.0.0
docker push registry.example.com/apartment_frontend:1.0.0

# Deploy on production server
docker pull registry.example.com/apartment_backend:1.0.0
docker pull registry.example.com/apartment_frontend:1.0.0
docker-compose up -d
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (deployment.yml, service.yml, ingress.yml, etc.)

### Scaling

**Horizontal Scaling:**
- Nginx load balancer for multiple backend instances
- Backend services with replicas in docker-compose or Kubernetes
- PostgreSQL connection pooling (PgBouncer)

**Vertical Scaling:**
- Increase resource limits in docker-compose
- Database query optimization with indexes
- Caching strategy optimization

---

## Support & Contact

For issues or questions:
1. Check Troubleshooting section
2. Review application logs: `docker-compose logs -f`
3. Check API documentation: http://localhost:8000/docs

---

**Last Updated:** May 2026
**Version:** 1.0.0
**Status:** Production Ready ✓
