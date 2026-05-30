from bson import ObjectId
from database import notifications_collection, users_collection


async def get_user_notifications(current_user: dict):
    """Get notifications for the current user"""
    notifications = list(notifications_collection.find(
        {"user_id": str(current_user["_id"])}
    ).sort("created_at", -1).limit(50))
    
    result = []
    for notif in notifications:
        source_user = users_collection.find_one({"_id": ObjectId(notif["source_user_id"])})
        result.append({
            "notification_id": str(notif["_id"]),
            "type": notif["type"],
            "source_username": source_user["username"] if source_user else "Unknown",
            "source_profile_image": source_user.get("profile_image_url", "") if source_user else "",
            "post_id": notif.get("post_id"),
            "is_read": notif.get("is_read", False),
            "created_at": notif["created_at"].isoformat()
        })
    
    return result


