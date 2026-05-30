from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Request Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    bio: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


# Response Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str


class UserProfile(BaseModel):
    user_id: str
    username: str
    bio: str
    profile_image_url: str
    followers_count: int
    following_count: int
    posts_count: int
    is_following: bool


class PostResponse(BaseModel):
    post_id: str
    user_id: str
    username: str
    profile_image_url: str
    image_url: str
    caption: str
    likes_count: int
    comments_count: int
    is_liked: bool
    created_at: str


class CommentResponse(BaseModel):
    comment_id: str
    user_id: str
    username: str
    profile_image_url: str
    comment_text: str
    created_at: str


class NotificationResponse(BaseModel):
    notification_id: str
    type: str
    source_username: str
    source_profile_image: str
    post_id: Optional[str]
    is_read: bool
    created_at: str


