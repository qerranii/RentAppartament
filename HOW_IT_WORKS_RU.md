# Как это работает? - ApartmentForRent

## Полное объяснение потока данных и интеграции

### Содержание
1. [Начало сеанса](#начало-сеанса)
2. [Регистрация и вход](#регистрация-и-вход)
3. [Создание прогноза](#создание-прогноза)
4. [Обработка данных](#обработка-данных)
5. [ML inference](#ml-inference)
6. [Сохранение результата](#сохранение-результата)
7. [Отображение результата](#отображение-результата)

---

## Начало сеанса

### 1. Пользователь открывает приложение

```
User Browser (http://localhost:3000)
           ↓
    Next.js Frontend Loading
           ↓
    Check localStorage for tokens
           ├─ Token found? → Load user data from Zustand store
           ├─ Token not found? → Show landing page with Login/Register
           └─ Token expired? → Show login page
```

### 2. Nginx reverse proxy

При открытии http://localhost:80 (или http://localhost):

```
Request: GET /
           ↓
    Nginx (Port 80)
    ├─ Match location: /api/ → proxy_pass http://backend/ (strip /api/)
    ├─ Match location: /uploads/ → serve static files
    ├─ Match location: / → proxy_pass http://frontend:3000
    └─ Response from frontend (Next.js)
           ↓
    Browser renders page
```

---

## Регистрация и вход

### Поток регистрации

```
Frontend Form
├─ Input: email, password, full_name
├─ Validate: email format, password length (min 8)
└─ Submit
      ↓
POST http://localhost:8000/api/auth/register
    (via Nginx: POST http://localhost/api/auth/register)
      ↓
Nginx (/api/ → strip and forward to backend:8000)
      ↓
Backend FastAPI
├─ Receive: {email, password, full_name}
├─ Validate input using Pydantic schema
├─ Check if user already exists in DB
│  ├─ Yes → Return 409 Conflict
│  └─ No → Continue
├─ Hash password using bcrypt
├─ Create user in PostgreSQL
├─ Generate tokens using PyJWT:
│  ├─ access_token: expires in 30 minutes
│  └─ refresh_token: expires in 7 days
└─ Return: {access_token, refresh_token, token_type: "bearer"}
      ↓
Frontend
├─ Save tokens in localStorage
├─ Update Zustand auth store with user
└─ Redirect to /dashboard
```

### Поток входа

```
Frontend Login Form
├─ Input: email, password
└─ Submit
      ↓
POST /api/auth/login {email, password}
      ↓
Backend FastAPI
├─ Find user by email in PostgreSQL
├─ If not found → Return 401 Unauthorized
├─ Compare password with bcrypt hash
├─ If mismatch → Return 401 Unauthorized
├─ Generate new tokens
└─ Return: {access_token, refresh_token, ...}
      ↓
Frontend stores tokens and redirects to /dashboard
```

---

## Создание прогноза

### 1. Пользователь заполняет форму на Dashboard

```
Dashboard Form
├─ Fields (27 total):
│  ├─ title: "Apartment in Moscow"
│  ├─ description: "Nice apartment with furniture and WiFi"
│  ├─ region: "Moscow"
│  ├─ city: "Moscow"
│  ├─ metro: "Red Square"
│  ├─ street_type: "улица"
│  ├─ square: 50 (m²)
│  ├─ rooms_clean: 2
│  ├─ floor: 2
│  ├─ max_floor: 5
│  ├─ time_to_metro: 10 (minutes)
│  ├─ has_furniture: true
│  ├─ has_appliances: true
│  ├─ has_wifi: true
│  ├─ has_parking: false
│  ├─ renovation_euro: true
│  ├─ pets_allowed: false
│  ├─ children_allowed: true
│  ├─ is_new_building: false
│  ├─ floor_category: "middle"
│  ├─ building_height: "mid_rise"
│  ├─ size_category: "medium"
│  ├─ metro_accessibility: "close"
│  └─ ... (other optional fields)
├─ Frontend validation: Pydantic schema matching
└─ Submit form
```

### 2. Отправка на backend

```
Frontend (handleCreatePrediction)
├─ Serialize form data to JSON
├─ Get token from localStorage
├─ Create HTTP request:
│  ├─ Method: POST
│  ├─ URL: /api/predictions
│  ├─ Headers: {
│  │   Content-Type: application/json,
│  │   Authorization: Bearer {access_token}
│  │ }
│  └─ Body: {form data as JSON}
└─ Send via Axios

      ↓

Axios Interceptor (Request)
├─ Check if token exists in localStorage
├─ Add: Authorization: Bearer {token}
└─ Forward request

      ↓

Nginx Reverse Proxy
├─ Receive: POST /api/predictions
├─ Strip /api/ prefix → /predictions
├─ Forward to: http://backend:8000/predictions
└─ Forward headers and body as-is

      ↓

Backend FastAPI (Uvicorn)
├─ Receive HTTP request
├─ Route to: POST /predictions endpoint
├─ Parse body: PredictionCreate schema
└─ Execute handler
```

---

## Обработка данных

### 1. Валидация в Backend

```
FastAPI Endpoint Handler
├─ Dependency injection: get_current_user
│  ├─ Extract token from Authorization header
│  ├─ Verify JWT signature using SECRET_KEY
│  ├─ Check token expiration
│  ├─ If invalid → Return 401 Unauthorized
│  └─ Load user from database
├─ Get database session: Depends(get_db)
├─ Validate request data with Pydantic
│  ├─ Check all required fields present
│  ├─ Validate types (str, int, float, bool)
│  ├─ Validate field ranges (room >= 1, square > 0, etc.)
│  └─ If invalid → Return 422 Unprocessable Entity
└─ Continue to service layer
```

### 2. Создание Service и инициализация ML

```
PredictionService.__init__
├─ Load database connection
├─ Load ML model dictionary via ModelLoader.get_model()
│  └─ If first time: load from rental_price_model.pkl
├─ Initialize FeaturePreprocessor with model components:
│  ├─ selected_features: list of 76 feature names
│  ├─ tfidf_vectorizer: TfidfVectorizer for text
│  ├─ target_encoder: TargetEncoder for categories
│  └─ russian_stopwords: set of 159 words to remove
└─ Get final_model: CatBoostRegressor
```

### 3. Feature Preprocessing - Сердце интеграции

```
FeaturePreprocessor.preprocess(raw_input_data)

Step 1: Численные признаки
├─ square = 50 (raw from input)
├─ floor = 2
├─ max_floor = 5
├─ rooms_clean = 2
├─ time_to_metro = 10
└─ [5 features prepared]

Step 2: Производные численные признаки
├─ floor_ratio = 2 / 5 = 0.4
├─ rooms_per_square = 2 / 50 = 0.04
├─ square_x_rooms = 50 * 2 = 100
├─ log_square = log(50 + 1) = 3.93
└─ [4 derived features]

Step 3: Целевое кодирование категорий (TargetEncoder)
├─ region "Moscow" → target_encoder lookup → 350 (mean price for Moscow region)
├─ city "Moscow" → 380 (mean price for Moscow city)
├─ metro "Red Square" → 400 (mean price near Red Square)
├─ street_type "улица" → 360
└─ [4 encoded features]

Step 4: Булевы признаки (0/1)
├─ is_first_floor = 0
├─ is_last_floor = 0
├─ has_furniture = 1
├─ has_appliances = 1
├─ has_tv = 0
├─ has_wifi = 1
├─ has_dishwasher = 0
├─ has_washing_machine = 0
├─ renovation_euro = 1
├─ renovation_cosmetic = 0
├─ renovation_new = 0
├─ pets_allowed = 0
├─ children_allowed = 1
├─ has_parking = 0
├─ has_balcony = 0
├─ has_security = 0
├─ is_new_building = 0
├─ has_metro = 1
├─ is_central = 0
└─ [20 boolean features]

Step 5: One-hot кодирование категорий
├─ floor_category = "middle"
│  ├─ floor_category_low = 0
│  ├─ floor_category_middle = 1
│  └─ floor_category_high = 0
├─ building_height = "mid_rise"
│  ├─ building_height_mid_rise = 1
│  ├─ building_height_high_rise = 0
│  └─ building_height_skyscraper = 0
├─ size_category = "medium"
│  ├─ size_category_small = 0
│  ├─ size_category_medium = 1
│  ├─ size_category_large = 0
│  └─ size_category_huge = 0
├─ metro_accessibility = "close"
│  ├─ metro_accessibility_close = 1
│  ├─ metro_accessibility_medium = 0
│  └─ metro_accessibility_far = 0
└─ [16 one-hot features]

Step 6: Текстовая обработка (TF-IDF)
├─ description = "Nice apartment with furniture and WiFi"
├─ Очистка текста:
│  ├─ Нижний регистр: "nice apartment with furniture and wifi"
│  ├─ Удаление русских стоп-слов (and, with, etc.)
│  └─ Результат: "nice apartment furniture wifi"
├─ TfidfVectorizer.transform(cleaned_text)
│  └─ Вычисляет TF-IDF вес для каждого термина
├─ Результат: 30 TF-IDF признаков
│  ├─ tfidf_0 = 0.25 (weight of some word)
│  ├─ tfidf_1 = 0.15
│  ├─ ...
│  └─ tfidf_29 = 0.0 (unused feature)
└─ [30 TF-IDF features]

ИТОГО: 5 + 4 + 4 + 20 + 16 + 30 = 79 признаков
  → Отбор K-лучших: SelectKBest выбирает 76 из 79
  → Результат: NumPy array shape (1, 76)

[50, 2, 5, 2, 10, 0.4, 0.04, 100, 3.93, 350, 380, 400, 360, 0, 0, 1, 1, 0, 1, ... tfidf features ...]
```

---

## ML inference

### Модель предсказания цены

```
CatBoostRegressor.predict([76-element feature vector])

Internal CatBoost process:
├─ Load decision trees (2000 trees, depth=8)
├─ For each tree:
│  ├─ Navigate through tree nodes based on feature values
│  ├─ Output leaf prediction value
│  └─ Weight by learning_rate (0.03)
├─ Sum all predictions: sum(tree_1 + tree_2 + ... + tree_2000)
└─ Return: final prediction (float)

Example output: 45250.75 RUB per month

Performance:
├─ Inference time: ~5-10 ms per prediction
├─ Expected accuracy: ±15% (based on validation RMSE)
└─ Output range: 20,000 - 500,000 RUB
```

---

## Сохранение результата

### 1. Сохранение в базе данных

```
After model.predict() returns price

PredictionService.create_prediction()
├─ Prepare data dict:
│  ├─ user_id = current_user.id (from JWT)
│  ├─ title = from input
│  ├─ description = from input
│  ├─ region = from input
│  ├─ city = from input
│  ├─ metro = from input
│  ├─ street_type = from input
│  ├─ square = from input
│  ├─ rooms_clean = from input
│  ├─ floor = from input
│  ├─ max_floor = from input
│  ├─ time_to_metro = from input
│  ├─ predicted_price = model output (45250.75)
│  ├─ confidence_score = null (model doesn't provide)
│  └─ timestamps = auto set by DB
├─ Insert into PostgreSQL via SQLAlchemy ORM
│  └─ INSERT INTO predictions (user_id, title, region, ...)
│          VALUES (1, 'Apartment in Moscow', 'Moscow', ...)
├─ Get generated prediction.id = 42
└─ Return prediction object to response handler
```

### 2. Формирование Response

```
API Response Handler
├─ Convert Prediction ORM object to Pydantic Response schema
├─ Serialize to JSON:
│  {
│    "id": 42,
│    "user_id": 1,
│    "title": "Apartment in Moscow",
│    "description": "Nice apartment with furniture and WiFi",
│    "region": "Moscow",
│    "city": "Moscow",
│    "metro": "Red Square",
│    "street_type": "улица",
│    "square": 50,
│    "rooms_clean": 2,
│    "floor": 2,
│    "max_floor": 5,
│    "time_to_metro": 10,
│    "predicted_price": 45250.75,
│    "confidence_score": null,
│    "created_at": "2026-05-21T15:30:45.123Z",
│    "updated_at": "2026-05-21T15:30:45.123Z",
│    "images": []
│  }
├─ Set HTTP status: 201 Created
└─ Send JSON response
```

### 3. Передача через Nginx

```
Backend sends HTTP response
         ↓
Nginx receives response
├─ Strip any internal headers
├─ Add security headers:
│  ├─ X-Frame-Options: SAMEORIGIN
│  ├─ X-Content-Type-Options: nosniff
│  └─ X-XSS-Protection: 1; mode=block
└─ Forward to client

Response headers
├─ HTTP/1.1 201 Created
├─ Content-Type: application/json
├─ Content-Length: 523
└─ ... other headers ...
```

---

## Отображение результата

### 1. Frontend получает ответ

```
Axios Response Interceptor
├─ Status 201 Created
├─ Body: JSON prediction object
└─ Return resolved Promise

handleCreatePrediction catch block
├─ Response successful
├─ Update predictions array: [new_prediction, ...old_predictions]
├─ Clear form fields
└─ Continue...
```

### 2. Toast уведомление

```
toast.success(`Prediction created! Price: ₽${data.predicted_price.toFixed(0)}`)

Browser notification
├─ Type: Success (green)
├─ Message: "Prediction created! Price: ₽45251"
├─ Display duration: 4 seconds
└─ Auto-dismiss
```

### 3. Обновление UI

```
React State Update
├─ setPredictions([new_prediction, ...predictions])
│  └─ React re-renders the predictions table
├─ setNewPrediction({...reset form})
│  └─ Clear all form inputs
└─ Component re-render

Table updates
├─ New row added to top: prediction ID 42
├─ Display: Title, City, Price ₽45251, Area 50m²
├─ Add action buttons: View, Delete
└─ User sees result immediately
```

### 4. Полный цикл отображения

```
User fills form (27 fields)
         ↓
Click "Create Prediction" button
         ↓
Frontend validation ✓
         ↓
POST /api/predictions with JWT token
         ↓
Nginx routes to Backend
         ↓
Backend validates request ✓
         ↓
Load ML model + components (cached)
         ↓
Preprocess 27 inputs → 76 features ✓
         ↓
CatBoost model inference → 45250.75
         ↓
Save to PostgreSQL ✓
         ↓
Return 201 Created with prediction object
         ↓
Nginx forwards response
         ↓
Frontend receives response
         ↓
Display toast: "Prediction created! Price: ₽45251"
         ↓
Update table with new prediction
         ↓
User sees prediction in dashboard table
         ↓
Total time: ~500-1000ms
```

---

## Дополнительные функции

### Получение списка прогнозов

```
User clicks on Dashboard
         ↓
useEffect hook runs
         ↓
GET /api/predictions?skip=0&limit=20 + JWT token
         ↓
Backend:
├─ Get current user from JWT
├─ Query: SELECT * FROM predictions WHERE user_id = 1 LIMIT 20
├─ Return list of predictions
└─ Convert to Response schema

Frontend:
├─ setPredictions([...])
└─ Render table with all predictions
```

### Удаление прогноза

```
User clicks Delete on row
         ↓
Confirm dialog
         ↓
DELETE /api/predictions/{prediction_id} + JWT token
         ↓
Backend:
├─ Verify ownership (prediction.user_id == current_user.id)
├─ DELETE FROM predictions WHERE id = 42 AND user_id = 1
├─ Cascade: delete images, logs
└─ Return 204 No Content

Frontend:
├─ Remove prediction from array
├─ Re-render table
└─ Show success toast
```

### Аналитика

```
User navigates to /analytics
         ↓
GET /api/predictions/stats/analytics + JWT token
         ↓
Backend:
├─ Get all predictions for user
├─ Calculate: COUNT, AVG, MIN, MAX, MEDIAN
└─ Return statistics

Frontend:
├─ Render graphs with Recharts
├─ Display: avg price, distribution chart
└─ Show "10 predictions, avg ₽48,000/mo"
```

---

## Architecture Diagram (Data Flow)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Browser                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           Next.js Frontend (React)                          │   │
│  │  ├─ Dashboard Form (27 input fields)                       │   │
│  │  ├─ Predictions Table                                      │   │
│  │  └─ Analytics Charts                                       │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                         │                                           │
│                         │ HTTP/REST                                │
│                         │ JSON + JWT Token                         │
│                         └──────────────────┐                       │
└────────────────────────────────────────────┼───────────────────────┘
                                             │
                   ┌─────────────────────────▼────────────────────┐
                   │  Nginx Reverse Proxy (Port 80)              │
                   │  ├─ /api/* → Backend                         │
                   │  ├─ /uploads/* → Static files               │
                   │  └─ / → Frontend                             │
                   └─────────────────────────┬────────────────────┘
                                             │
                ┌────────────────────────────▼─────────────────────────┐
                │   Backend FastAPI (Port 8000, Uvicorn)             │
                │                                                     │
                │  POST /predictions Handler                         │
                │  ├─ [1] Validate JWT Token                        │
                │  ├─ [2] Parse & Validate Input (Pydantic)        │
                │  │                                                │
                │  ├─ [3] Feature Preprocessing                    │
                │  │      (FeaturePreprocessor)                   │
                │  │      • Numerical: 5 + 4 derived             │
                │  │      • Encoded: 4 (TargetEncoder)           │
                │  │      • Boolean: 20                          │
                │  │      • One-hot: 16                          │
                │  │      • TF-IDF: 30 (from description)        │
                │  │      → 76 features total                   │
                │  │                                                │
                │  ├─ [4] ML Model Inference                      │
                │  │      CatBoostRegressor.predict(features)    │
                │  │      → price = 45250.75                    │
                │  │                                                │
                │  ├─ [5] Save to PostgreSQL                      │
                │  │      INSERT INTO predictions (...)          │
                │  │                                                │
                │  └─ [6] Return Response (JSON, 201 Created)    │
                │                                                     │
                └────────────────────────────┬─────────────────────────┘
                       │                     │
        ┌──────────────┼─────┐    ┌─────────┼──────────┐
        │              │     │    │         │          │
        ▼              ▼     ▼    ▼         ▼          ▼
    ┌────────┐  ┌─────────┐ ┌────────┐ ┌────────┐  ┌────────┐
    │Postgres│  │ Redis   │ │RabbitMQ│ │Prometheus│Grafana │
    │ (5432) │  │ (6379)  │ │(5672)  │ │(9090)    │(8080)  │
    │        │  │         │ │        │ │          │        │
    │Users   │  │Tokens   │ │Celery  │ │Metrics   │Dashbrd │
    │Predict-│  │Cache    │ │Tasks   │ │          │        │
    │ions    │  │Sessions │ │        │ │          │        │
    └────────┘  └─────────┘ └────────┘ └────────┘  └────────┘
```

---

## Жизненный цикл ML Model

### Инициализация (First Request)

```
First prediction request arrives
         ↓
FastAPI startup handler runs (lifespan event)
├─ Load ML model once
├─ Parse rental_price_model.pkl
├─ Extract components:
│  ├─ final_model: CatBoostRegressor
│  ├─ tfidf_vectorizer: TfidfVectorizer
│  ├─ target_encoder: TargetEncoder
│  ├─ selected_features: [76 names]
│  └─ russian_stopwords: {159 words}
├─ Cache in memory (singleton)
└─ ModelLoader._model_dict = {everything}

Subsequent requests:
├─ ModelLoader.get_model() returns cached dict
└─ No file I/O needed (fast)
```

### Per-Request Flow

```
Request arrives
         ↓
FeaturePreprocessor initialized with cached model_dict
         ↓
Features transformed through pipeline
         ↓
model_dict['final_model'].predict(features)
         ↓
Inference result returned
         ↓
FAST: ~10ms per prediction
```

---

## Summary

The complete flow from user form submission to displayed prediction result:

1. **User fills form** → 27 parameters
2. **Frontend validates** → Type & range checks
3. **HTTP request** → POST /api/predictions (+ JWT)
4. **Nginx routes** → Strips /api/ prefix
5. **Backend validates** → Pydantic schema
6. **Feature preprocessing** → 27 inputs → 76 features
7. **ML inference** → CatBoost prediction
8. **Database save** → PostgreSQL INSERT
9. **HTTP response** → 201 Created (JSON)
10. **Frontend displays** → Table update + toast
11. **User sees price** → ✓ Complete

**Total Time:** 500-1000ms (mostly inference + database roundtrip)

---

**Версия:** 1.0.0
**Статус:** Production Ready ✓
**Дата:** May 2026
