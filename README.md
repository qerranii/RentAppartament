# ApartmentForRent — Платформа прогнозирования цен на аренду квартир

## Оглавление

1. Архитектура
2. Стек технологий
3. Структура проекта
4. Запуск приложения
5. Backend API
6. Frontend
7. Интеграция ML-модели
8. Docker и инфраструктура
9. Troubleshooting
10. Deployment

---

# Архитектура

## Общая архитектура системы

```text
┌──────────────────────────────────────────────────────────────┐
│                         Internet                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │        Nginx :80           │
                │  • Reverse Proxy           │
                │  • Static files            │
                │  • API Routing             │
                └────────────────────────────┘
                         │          │
              ┌──────────┘          └──────────┐
              ▼                                ▼

      ┌────────────────┐              ┌────────────────┐
      │ Frontend:3000  │              │ Backend:8000   │
      │ Next.js/React  │              │ FastAPI        │
      │                │              │                │
      │ • Auth         │              │ • Auth API     │
      │ • Dashboard    │              │ • Predictions  │
      │ • Analytics    │              │ • ML Inference │
      └────────────────┘              └────────────────┘
                                                │
          ┌─────────────────────────────────────┼────────────────────────────┐
          ▼                                     ▼                            ▼

┌──────────────────┐                ┌──────────────────┐        ┌──────────────────┐
│ PostgreSQL       │                │ Redis            │        │ RabbitMQ         │
│                  │                │                  │        │                  │
│ • Users          │                │ • Cache          │        │ • Celery Tasks   │
│ • Predictions    │                │ • Sessions       │        │ • Async Jobs     │
│ • Images         │                │ • Tokens         │        │                  │
│ • Logs           │                │                  │        │                  │
└──────────────────┘                └──────────────────┘        └──────────────────┘
          │
          ▼

┌────────────────────────────────────┐
│            ML Model                │
│         CatBoostRegressor          │
│                                    │
│ • 76 features                      │
│ • RMSE loss                        │
│ • 2000 iterations                  │
└────────────────────────────────────┘
```

---

## Поток данных для прогнозирования

```text
Frontend (Dashboard)
        │
        │ POST /api/predictions
        ▼

Nginx Reverse Proxy
        │
        ▼

Backend (FastAPI)
        │
        ├── 1. Валидация входных данных
        │
        ├── 2. Feature Engineering
        │       • Numerical features
        │       • Derived features
        │       • Target Encoding
        │       • TF-IDF
        │       • One-Hot Encoding
        │
        ├── 3. ML Inference
        │       model.predict(features)
        │
        ├── 4. Сохранение в PostgreSQL
        │
        └── 5. Возврат результата

Frontend
        │
        └── Отображение цены аренды
```

---

# Стек технологий

## Backend

| Технология | Назначение |
|---|---|
| FastAPI 0.104.1 | Асинхронный web framework |
| Uvicorn 0.24.0 | ASGI сервер |
| SQLAlchemy 2.0.23 | ORM |
| AsyncPG 0.29.0 | PostgreSQL драйвер |
| Pydantic 2.5.3 | Валидация данных |
| CatBoost 1.2.5 | ML модель |
| scikit-learn 1.3.2 | Feature preprocessing |
| Celery 5.3.4 | Async task queue |
| Redis 5.0.1 | Кэширование |

---

## Frontend

| Технология | Назначение |
|---|---|
| Next.js 15 | React framework |
| React 18.2 | UI библиотека |
| TypeScript 5.6 | Типизация |
| Axios 1.6 | HTTP client |
| TailwindCSS 3.4 | Стили |
| Zustand 4.4 | State management |
| React Hot Toast 2.4 | Notifications |

---

## Infrastructure

| Технология | Назначение |
|---|---|
| PostgreSQL 16 | База данных |
| Redis 7 | In-memory cache |
| RabbitMQ 3.13 | Message Broker |
| Nginx | Reverse Proxy |
| Docker | Контейнеризация |
| Prometheus | Мониторинг |
| Grafana | Метрики |

---

# Структура проекта

```text
ApartmentForRent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── predictions/
│   │   │   └── uploads/
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── constants.py
│   │   │
│   │   ├── ml/
│   │   │   └── model_loader.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   │
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── utils/
│   │   ├── workers/
│   │   └── tests/
│   │
│   ├── migrations/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── utils/
│   │
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── nginx/
├── prometheus/
├── docker-compose.yml
├── rental_price_model.pkl
└── README.md
```

---

# Запуск приложения

## Требования

### Вариант 1

- Docker
- Docker Compose

### Вариант 2

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7

---

# Локальный запуск

## Установка зависимостей

### Backend

```bash
pip install -r backend/requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## Запуск Backend

```bash
cd backend

export MODEL_PATH=../rental_price_model.pkl
export DATABASE_URL=postgresql://apartment_user:password@localhost:5432/apartment_rent
export DEBUG=False

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Backend URLs

```text
http://localhost:8000
```

### Swagger Docs

```text
http://localhost:8000/docs
```

---

## Запуск Frontend

```bash
export NEXT_PUBLIC_API_URL=http://localhost:8000/api

npm run dev
```

### Frontend URL

```text
http://localhost:3000
```

---

# Docker Compose запуск

## Запуск всех сервисов

```bash
docker-compose up -d
```

## Проверка статуса

```bash
docker-compose ps
```

## Просмотр логов

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Остановка

```bash
docker-compose down
```

---

## Доступные сервисы

| Сервис | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Nginx | http://localhost |
| Swagger Docs | http://localhost/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:8080 |

---

# Backend API

# Authentication API

## POST /auth/register

Регистрация пользователя.

### Request

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### Response

```json
{
  "access_token": "jwt-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer"
}
```

---

## POST /auth/login

Авторизация пользователя.

### Request

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Response

```json
{
  "access_token": "jwt-token",
  "refresh_token": "jwt-refresh-token",
  "token_type": "bearer"
}
```

---

## POST /auth/refresh

Обновление access token.

### Request

```json
{
  "refresh_token": "jwt-refresh-token"
}
```

---

# Predictions API

## POST /predictions

Создание прогноза стоимости аренды.

### Request

```json
{
  "title": "Apartment in Moscow",
  "description": "Nice apartment",
  "region": "Moscow",
  "city": "Moscow",
  "metro": "Red Square",
  "square": 50,
  "rooms_clean": 2,
  "floor": 2,
  "max_floor": 5,
  "time_to_metro": 10
}
```

### Response

```json
{
  "id": 1,
  "predicted_price": 50000.50,
  "created_at": "2026-05-21T15:00:00Z"
}
```

---

## GET /predictions

Получение списка прогнозов.

### Query Parameters

| Параметр | Описание |
|---|---|
| skip | Смещение |
| limit | Количество записей |

---

## GET /predictions/{id}

Получение детальной информации.

---

## DELETE /predictions/{id}

Удаление прогноза.

---

## GET /predictions/stats/analytics

Получение аналитики.

### Response

```json
{
  "total": 10,
  "avg_price": 48000,
  "min_price": 35000,
  "max_price": 65000,
  "median_price": 50000
}
```

---

# Health Check

## GET /health

### Response

```json
{
  "status": "healthy",
  "app": "ApartmentForRent",
  "version": "1.0.0"
}
```

---

# Frontend

# Структура страниц

## Главная страница (/)

- Информация о приложении
- Login/Register
- Dashboard link

---

## Register (/auth/register)

- Email validation
- Password validation
- Redirect на dashboard

---

## Login (/auth/login)

- Авторизация
- Remember me
- Redirect

---

## Dashboard (/dashboard)

### Форма прогнозирования

- Inputs
- Validation
- Loading state
- Submit button

### Таблица прогнозов

- Pagination
- Delete/View actions
- История прогнозов

---

## Analytics (/analytics)

- Графики
- Статистика
- Charts по регионам

---

# State Management

## Zustand Store

```typescript
{
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
}
```

---

# API Client

```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});
```

---

# Интеграция ML-модели

# Архитектура модели

## CatBoostRegressor

### Параметры обучения

| Параметр | Значение |
|---|---|
| Iterations | 2000 |
| Learning Rate | 0.03 |
| Depth | 8 |
| Loss Function | RMSE |

---

# Признаки модели

## Numerical Features

- square
- floor
- max_floor
- rooms_clean
- time_to_metro

---

## Derived Features

- floor_ratio
- rooms_per_square
- square_x_rooms
- log_square

---

## Boolean Features

- has_furniture
- has_wifi
- has_parking
- pets_allowed
- children_allowed

---

## TF-IDF Features

- 30 текстовых признаков
- Описание квартиры
- Удаление stopwords

---

# Pipeline обработки

```python
# Validation
validate_required_fields()

# Feature Engineering
generate_features()

# Encoding
target_encoding()

# TF-IDF
text_processing()

# Build Vector
build_feature_vector()

# Predict
model.predict()
```

---

# Производительность модели

| Метрика | Значение |
|---|---|
| R² Score | 0.85+ |
| RMSE | ~8000 RUB |
| MAE | ~6000 RUB |

---

# Docker и инфраструктура

# Docker Compose Services

## PostgreSQL

```yaml
Container: apartment_postgres
Port: 5432
Volumes:
  - postgres_data
```

---

## Redis

```yaml
Container: apartment_redis
Port: 6379
```

---

## RabbitMQ

```yaml
Container: apartment_rabbitmq
Ports:
  - 5672
  - 15672
```

---

## Backend

```yaml
Container: apartment_backend
Port: 8000
Command:
  uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Frontend

```yaml
Container: apartment_frontend
Port: 3000
Command:
  npm start
```

---

## Nginx

```yaml
Container: apartment_nginx
Ports:
  - 80
  - 443
```

---

## Prometheus

```yaml
Container: apartment_prometheus
Port: 9090
```

---

## Grafana

```yaml
Container: apartment_grafana
Port: 8080
```

---

# Network

## Bridge Network

```text
apartment_network
```

---

# Volumes

- postgres_data
- redis_data
- rabbitmq_data
- prometheus_data
- uploads

---

# Troubleshooting

# Backend не запускается

## Ошибка

```text
Model not found at /app/rental_price_model.pkl
```

## Решение

```yaml
volumes:
  - ./rental_price_model.pkl:/app/rental_price_model.pkl
```

---

# PostgreSQL connection error

## Ошибка

```text
psycopg2.OperationalError
```

## Решение

```bash
docker-compose ps postgres
docker-compose logs postgres
```

---

# Frontend не загружается

## Ошибка

```text
Failed to load predictions
```

## Решение

```bash
curl http://localhost:8000/health
```

---

# Migration errors

## Ошибка

```text
Alembic version ID is not set
```

## Решение

```bash
cd backend
alembic upgrade head
```

---

# Redis/RabbitMQ connection errors

## Ошибка

```text
ConnectionRefusedError
```

## Решение

```bash
docker-compose restart redis rabbitmq
```

---

# Deployment

# Production Checklist

- [ ] DEBUG=False
- [ ] Новый SECRET_KEY
- [ ] SSL/TLS сертификаты
- [ ] Backup базы данных
- [ ] Monitoring
- [ ] Load testing

---

# Environment Variables

```env
APP_NAME=ApartmentForRent
DEBUG=False
VERSION=1.0.0

HOST=0.0.0.0
PORT=8000

DATABASE_URL=postgresql://user:password@db:5432/apartment_rent

REDIS_URL=redis://redis:6379/0

SECRET_KEY=super-secret-key

ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=["https://yourdomain.com"]
```

---

# Docker Registry Deployment

```bash
docker-compose build

docker push registry.example.com/apartment_backend:1.0.0
docker push registry.example.com/apartment_frontend:1.0.0
```

---

# Kubernetes Deployment

```text
k8s/
├── deployment.yml
├── service.yml
├── ingress.yml
```

---

# Масштабирование

## Horizontal Scaling

- Несколько backend-инстансов
- Load Balancer
- PgBouncer

---

## Vertical Scaling

- Увеличение CPU/RAM
- SQL optimization
- Cache optimization

---

# Полезные команды

## Логи

```bash
docker-compose logs -f
```

## Статус контейнеров

```bash
docker-compose ps
```

## Перезапуск Redis и RabbitMQ

```bash
docker-compose restart redis rabbitmq
```

---

# Контакты и поддержка

1. Проверьте раздел Troubleshooting
2. Изучите логи контейнеров
3. Используйте Swagger Docs
