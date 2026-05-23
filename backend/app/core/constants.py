"""Application constants."""

# Prediction Districts
DISTRICTS = [
    "Downtown", "Midtown", "Uptown", "East Side", "West Side",
    "North End", "South End", "Central", "Suburbs", "Rural"
]

# Image Upload
IMAGE_QUALITY = 85
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1440
IMAGE_THUMBNAIL_SIZE = (300, 300)

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Prediction Cache
PREDICTION_CACHE_KEY = "prediction:{user_id}:{prediction_id}"
PREDICTION_LIST_CACHE_KEY = "predictions:{user_id}:page:{page}"

# Inference
INFERENCE_TIMEOUT = 30
BATCH_PREDICTION_SIZE = 32

# Room types
ROOM_TYPES = ["Studio", "1BR", "2BR", "3BR", "4BR", "5BR+"]

# Floor types
FLOOR_MIN = 1
FLOOR_MAX = 50
