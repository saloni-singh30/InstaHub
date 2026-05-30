import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "instahub")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# File Upload Configuration
UPLOAD_DIR = "uploads"
IMAGES_DIR = f"{UPLOAD_DIR}/images"
PROFILES_DIR = f"{UPLOAD_DIR}/profiles"
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
MAX_IMAGE_SIZE = (1080, 1080)


