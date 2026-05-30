from fastapi import HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import datetime
from bson import ObjectId
from auth import get_password_hash, create_access_token, verify_password
from database import users_collection
from utils import save_image


async def register_user(
    username: str,
    email: str,
    password: str,
    bio: Optional[str] = None,
    profile_image: Optional[UploadFile] = File(None)
):
    """Register a new user"""
    try:
        # Validate input
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="Username is required")
        if not email or not email.strip():
            raise HTTPException(status_code=400, detail="Email is required")
        if not password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Validate password
        password_str = str(password) if not isinstance(password, str) else password
        
        # Check minimum length
        if len(password_str) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check maximum byte length (bcrypt has 72-byte limit)
        # Note: We'll truncate in get_password_hash, but warn if very long
        password_bytes = password_str.encode('utf-8')
        if len(password_bytes) > 72:
            # Warn but don't fail - get_password_hash will truncate
            print(f"Warning: Password exceeds 72 bytes, will be truncated")
        
        # Check if user exists
        if users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        profile_image_url = None
        # Check if profile_image exists and has a filename
        if profile_image and hasattr(profile_image, 'filename') and profile_image.filename:
            try:
                profile_image_url = save_image(profile_image, "profiles")
            except Exception as e:
                # If image save fails, continue without profile image
                print(f"Warning: Failed to save profile image: {str(e)}")
                profile_image_url = None
        
        user = {
            "username": username.strip(),
            "email": email.strip().lower(),
            "password_hash": get_password_hash(password_str),
            "bio": (bio or "").strip(),
            "profile_image_url": profile_image_url or "",
            "followers": [],
            "following": [],
            "created_at": datetime.utcnow()
        }
        
        result = users_collection.insert_one(user)
        user_id = str(result.inserted_id)
        
        access_token = create_access_token(data={"sub": user_id})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "username": username
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error and re-raise as HTTPException
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


async def login_user(username: str, password: str):
    """Authenticate user and return JWT token"""
    user = users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "username": user["username"]
    }

