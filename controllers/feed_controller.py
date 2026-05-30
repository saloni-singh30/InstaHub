from bson import ObjectId
from database import posts_collection, users_collection, comments_collection


async def get_feed(current_user: dict):
    """Get feed posts from followed users"""
    following = current_user.get("following", [])
    following.append(str(current_user["_id"]))  # Include own posts
    
    posts = list(posts_collection.find({"user_id": {"$in": following}}).sort("created_at", -1).limit(50))
    
    result = []
    for post in posts:
        user = users_collection.find_one({"_id": ObjectId(post["user_id"])})
        liked = str(current_user["_id"]) in post.get("likes", [])
        
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


