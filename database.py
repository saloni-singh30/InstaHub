from pymongo import MongoClient
from config import MONGODB_URL, DATABASE_NAME

# MongoDB connection
client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Database collections
users_collection = db.users
posts_collection = db.posts
comments_collection = db.comments
notifications_collection = db.notifications


