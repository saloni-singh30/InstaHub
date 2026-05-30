# InstaHub MVP

An Instagram-like social media platform MVP focused on image sharing, basic profiles, and user interactions.

## Features

- User authentication (signup, login, logout)
- User profiles with bio and profile picture
- Post creation with image and caption
- Home feed showing followed users' posts
- Like and unlike posts
- Comment on posts
- Follow and unfollow users
- Basic notifications

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Storage**: Local file storage for images
- **Frontend**: HTML/CSS/JavaScript
- **Authentication**: JWT tokens

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally
- pip (Python package manager)

### Installation Steps

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up MongoDB:**
   - Make sure MongoDB is running locally on `mongodb://localhost:27017`
   - Or update the connection string in `.env` if using a different MongoDB instance

3. **Create environment file:**
   - Create a `.env` file in the project root with:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=instahub
SECRET_KEY=your-secret-key-here-change-in-production-use-random-string
```

4. **Run the server:**
   - **Windows:** Double-click `start.bat` or run:
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   - **Linux/Mac:** Run:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application:**
   - Open your browser and go to `http://localhost:8000`
   - The frontend will be served automatically
   - API documentation available at `http://localhost:8000/docs`

## API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /user/{id}` - Get user profile
- `POST /follow/{id}` - Follow or unfollow user
- `POST /posts` - Create post with image and caption
- `GET /feed` - Get posts from followed users
- `POST /posts/{id}/like` - Like or unlike a post
- `POST /posts/{id}/comment` - Add comment to post
- `GET /posts/{id}/comments` - Fetch comments of a post

## Developer

Saloni Singh

