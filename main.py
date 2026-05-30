from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import os

from config import IMAGES_DIR, PROFILES_DIR
from database import db
from auth import get_current_user
from controllers import (
    auth_controller,
    user_controller,
    post_controller,
    feed_controller,
    notification_controller
)

# Create FastAPI app
app = FastAPI(title="InstaHub MVP", version="1.0.0")

# CORS middleware - Allow all origins for development
# Note: When allow_credentials=True, you cannot use allow_origins=["*"]
# Since we use JWT tokens (not cookies), credentials aren't strictly needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create upload directories
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(PROFILES_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


# Root route
@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


# Authentication routes
@app.post("/auth/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    bio: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None)
):
    try:
        return await auth_controller.register_user(username, email, password, bio, profile_image)
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    return await auth_controller.login_user(username, password)


# User routes
@app.get("/user/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    return await user_controller.get_user_profile(user_id, current_user)


@app.get("/user/{user_id}/posts")
async def get_user_posts(user_id: str, current_user: dict = Depends(get_current_user)):
    return await user_controller.get_user_posts(user_id, current_user)


@app.post("/follow/{user_id}")
async def follow_user(user_id: str, current_user: dict = Depends(get_current_user)):
    return await user_controller.follow_unfollow_user(user_id, current_user)


@app.get("/search/users")
async def search_users(q: str, current_user: dict = Depends(get_current_user)):
    return await user_controller.search_users(q)


# Post routes
@app.post("/posts")
async def create_post(
    image: UploadFile = File(...),
    caption: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    return await post_controller.create_post(image, caption, current_user)


@app.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    return await post_controller.like_unlike_post(post_id, current_user)


@app.post("/posts/{post_id}/comment")
async def add_comment(
    post_id: str,
    comment_text: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    return await post_controller.add_comment(post_id, comment_text, current_user)


@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: str, current_user: dict = Depends(get_current_user)):
    return await post_controller.get_post_comments(post_id)


# Feed routes
@app.get("/feed")
async def get_feed(current_user: dict = Depends(get_current_user)):
    return await feed_controller.get_feed(current_user)


# Notification routes
@app.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    return await notification_controller.get_user_notifications(current_user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
