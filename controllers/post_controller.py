from fastapi import HTTPException, UploadFile, File, Form
from datetime import datetime
from bson import ObjectId
from database import posts_collection, comments_collection, users_collection, notifications_collection
from utils import save_image


async def create_post(image: UploadFile, caption: str, current_user: dict):
    """Create a new post with image and caption"""
    image_url = save_image(image, "images")
    
    post = {
        "user_id": str(current_user["_id"]),
        "image_url": image_url,
        "caption": caption,
        "likes": [],
        "created_at": datetime.utcnow()
    }
    
    result = posts_collection.insert_one(post)
    return {
        "post_id": str(result.inserted_id),
        "message": "Post created successfully"
    }


async def like_unlike_post(post_id: str, current_user: dict):
    """Like or unlike a post"""
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    user_id = str(current_user["_id"])
    likes = post.get("likes", [])
    
    if user_id in likes:
        # Unlike
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": user_id}}
        )
        return {"message": "Post unliked", "is_liked": False}
    else:
        # Like
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": user_id}}
        )
        
        # Create notification if not own post
        if post["user_id"] != user_id:
            notification = {
                "user_id": post["user_id"],
                "type": "like",
                "source_user_id": user_id,
                "post_id": post_id,
                "created_at": datetime.utcnow(),
                "is_read": False
            }
            notifications_collection.insert_one(notification)
        
        return {"message": "Post liked", "is_liked": True}


async def add_comment(post_id: str, comment_text: str, current_user: dict):
    """Add a comment to a post"""
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = {
        "post_id": post_id,
        "user_id": str(current_user["_id"]),
        "comment_text": comment_text,
        "created_at": datetime.utcnow()
    }
    
    result = comments_collection.insert_one(comment)
    
    # Create notification if not own post
    if post["user_id"] != str(current_user["_id"]):
        notification = {
            "user_id": post["user_id"],
            "type": "comment",
            "source_user_id": str(current_user["_id"]),
            "post_id": post_id,
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        notifications_collection.insert_one(notification)
    
    return {
        "comment_id": str(result.inserted_id),
        "message": "Comment added successfully"
    }


async def get_post_comments(post_id: str):
    """Get all comments for a post"""
    comments = list(comments_collection.find({"post_id": post_id}).sort("created_at", 1))
    
    result = []
    for comment in comments:
        user = users_collection.find_one({"_id": ObjectId(comment["user_id"])})
        result.append({
            "comment_id": str(comment["_id"]),
            "user_id": comment["user_id"],
            "username": user["username"] if user else "Unknown",
            "profile_image_url": user.get("profile_image_url", "") if user else "",
            "comment_text": comment["comment_text"],
            "created_at": comment["created_at"].isoformat()
        })
    
    return result


