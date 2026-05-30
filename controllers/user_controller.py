from fastapi import HTTPException
from bson import ObjectId
from database import users_collection, posts_collection


async def get_user_profile(user_id: str, current_user: dict):
    """Get user profile information"""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user posts count
    posts_count = posts_collection.count_documents({"user_id": user_id})
    
    # Check if current user follows this user
    is_following = str(current_user["_id"]) in user.get("followers", [])
    
    return {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "bio": user.get("bio", ""),
        "profile_image_url": user.get("profile_image_url", ""),
        "followers_count": len(user.get("followers", [])),
        "following_count": len(user.get("following", [])),
        "posts_count": posts_count,
        "is_following": is_following
    }


async def get_user_posts(user_id: str, current_user: dict):
    """Get all posts by a specific user"""
    posts = list(posts_collection.find({"user_id": user_id}).sort("created_at", -1))
    
    result = []
    for post in posts:
        user = users_collection.find_one({"_id": ObjectId(post["user_id"])})
        liked = str(current_user["_id"]) in post.get("likes", [])
        
        from database import comments_collection
        result.append({
            "post_id": str(post["_id"]),
            "user_id": post["user_id"],
            "username": user["username"] if user else "Unknown",
            "profile_image_url": user.get("profile_image_url", "") if user else "",
            "image_url": post["image_url"],
            "caption": post.get("caption", ""),
            "likes_count": len(post.get("likes", [])),
            "comments_count": comments_collection.count_documents({"post_id": str(post["_id"])}),
            "is_liked": liked,
            "created_at": post["created_at"].isoformat()
        })
    
    return result


async def follow_unfollow_user(user_id: str, current_user: dict):
    """Follow or unfollow a user"""
    from datetime import datetime
    from database import notifications_collection
    
    current_user_id = str(current_user["_id"])
    
    if current_user_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    target_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    followers = target_user.get("followers", [])
    
    if current_user_id in followers:
        # Unfollow
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"followers": current_user_id}}
        )
        users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$pull": {"following": user_id}}
        )
        return {"message": "Unfollowed successfully", "is_following": False}
    else:
        # Follow
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"followers": current_user_id}}
        )
        users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$addToSet": {"following": user_id}}
        )
        
        # Create notification
        notification = {
            "user_id": user_id,
            "type": "follow",
            "source_user_id": current_user_id,
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        notifications_collection.insert_one(notification)
        
        return {"message": "Followed successfully", "is_following": True}


async def search_users(query: str):
    """Search users by username"""
    users = list(users_collection.find({
        "username": {"$regex": query, "$options": "i"}
    }).limit(20))
    
    result = []
    for user in users:
        result.append({
            "user_id": str(user["_id"]),
            "username": user["username"],
            "profile_image_url": user.get("profile_image_url", ""),
            "bio": user.get("bio", "")
        })
    
    return result


