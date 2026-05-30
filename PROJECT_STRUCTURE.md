# InstaHub MVP - Project Structure

## Overview
This document describes the refactored project structure with separation of concerns.

## Directory Structure

```
saloni2/
├── main.py                      # Main FastAPI application entry point
├── config.py                    # Configuration settings
├── database.py                  # MongoDB connection and collections
├── auth.py                      # Authentication utilities (JWT, password hashing)
├── models.py                    # Pydantic models for request/response
├── utils.py                     # Utility functions (image handling)
├── controllers/                 # API route handlers (business logic)
│   ├── __init__.py
│   ├── auth_controller.py       # Authentication endpoints logic
│   ├── user_controller.py       # User profile and follow logic
│   ├── post_controller.py       # Post creation, likes, comments logic
│   ├── feed_controller.py       # Feed generation logic
│   └── notification_controller.py  # Notifications logic
├── frontend/                    # Frontend files
│   ├── index.html
│   ├── style.css
│   └── app.js
├── uploads/                     # Uploaded files
│   ├── images/                  # Post images
│   └── profiles/                # Profile pictures
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── VIVA_QUESTIONS.md            # Viva questions (beginner to advanced)
└── PROJECT_STRUCTURE.md         # This file
```

## File Descriptions

### Core Files

#### `main.py`
- FastAPI application initialization
- Route definitions (endpoints)
- Middleware configuration (CORS)
- Static file mounting
- Delegates business logic to controllers

#### `config.py`
- Centralized configuration
- Environment variables loading
- Constants (database URLs, secret keys, file paths)

#### `database.py`
- MongoDB client connection
- Database and collection references
- Single connection instance for reuse

#### `auth.py`
- Password hashing (bcrypt)
- JWT token creation and validation
- `get_current_user` dependency for protected routes

#### `models.py`
- Pydantic models for request/response validation
- Type definitions for API contracts

#### `utils.py`
- Image upload and processing
- File validation
- Image optimization (resizing)

### Controllers

#### `controllers/auth_controller.py`
- `register_user()` - User registration logic
- `login_user()` - User authentication logic

#### `controllers/user_controller.py`
- `get_user_profile()` - Fetch user profile
- `get_user_posts()` - Get user's posts
- `follow_unfollow_user()` - Follow/unfollow logic
- `search_users()` - User search functionality

#### `controllers/post_controller.py`
- `create_post()` - Create new post
- `like_unlike_post()` - Like/unlike toggle
- `add_comment()` - Add comment to post
- `get_post_comments()` - Fetch post comments

#### `controllers/feed_controller.py`
- `get_feed()` - Generate user feed from followed users

#### `controllers/notification_controller.py`
- `get_user_notifications()` - Fetch user notifications

## Benefits of This Structure

1. **Separation of Concerns**: Each file has a single responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Controllers can be tested independently
4. **Scalability**: Easy to add new features without cluttering main.py
5. **Reusability**: Utility functions and models can be reused
6. **Readability**: Clear organization makes code easier to understand

## API Endpoints

All endpoints are defined in `main.py` and delegate to controllers:

- `POST /auth/register` → `auth_controller.register_user()`
- `POST /auth/login` → `auth_controller.login_user()`
- `GET /user/{id}` → `user_controller.get_user_profile()`
- `GET /user/{id}/posts` → `user_controller.get_user_posts()`
- `POST /follow/{id}` → `user_controller.follow_unfollow_user()`
- `GET /search/users` → `user_controller.search_users()`
- `POST /posts` → `post_controller.create_post()`
- `POST /posts/{id}/like` → `post_controller.like_unlike_post()`
- `POST /posts/{id}/comment` → `post_controller.add_comment()`
- `GET /posts/{id}/comments` → `post_controller.get_post_comments()`
- `GET /feed` → `feed_controller.get_feed()`
- `GET /notifications` → `notification_controller.get_user_notifications()`

## Running the Project

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure MongoDB is running
3. Create `.env` file with configuration
4. Run: `python -m uvicorn main:app --reload`
5. Access: `http://localhost:8000`

## Notes

- All controllers are async functions
- Authentication is handled via `get_current_user` dependency
- Database operations use MongoDB's PyMongo driver
- Images are stored locally in `uploads/` directory
- Frontend communicates with backend via REST API


