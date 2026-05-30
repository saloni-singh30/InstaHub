import os
import shutil
from fastapi import UploadFile, HTTPException
from bson import ObjectId
from PIL import Image
from config import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE, IMAGES_DIR, PROFILES_DIR


def save_image(file: UploadFile, folder: str = "images") -> str:
    """Save uploaded image and return the URL path"""
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    filename = f"{ObjectId()}{file_ext}"
    
    if folder == "images":
        file_path = f"{IMAGES_DIR}/{filename}"
    elif folder == "profiles":
        file_path = f"{PROFILES_DIR}/{filename}"
    else:
        file_path = f"uploads/{folder}/{filename}"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Resize image if needed (optional optimization)
    try:
        img = Image.open(file_path)
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        img.save(file_path, optimize=True, quality=85)
    except Exception:
        pass
    
    return f"/uploads/{folder}/{filename}"


