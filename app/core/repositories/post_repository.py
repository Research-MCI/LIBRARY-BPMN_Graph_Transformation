from bson import ObjectId
from app.infrastructure.db.mongo_client import get_collection, mongo
from app.utils.logger import get_logger
from app.utils.exceptions.db_exceptions import NotFoundError, DatabaseException

logger = get_logger(__name__)
collection = get_collection("posts")


def create_post(data):
    try:
        result = collection.insert_one(data)
        logger.info(f"Post created: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise DatabaseException(str(e))


def get_post(post_id):
    try:
        obj_id = ObjectId(post_id)
        result = collection.find_one({"_id": obj_id})
        if not result:
            logger.warning(f"Post not found: {post_id}")
            raise NotFoundError("Post not found")
        return result
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching post: {e}")
        raise DatabaseException(str(e))


def update_post(post_id, data):
    try:
        obj_id = ObjectId(post_id)
        result = collection.update_one({"_id": obj_id}, {"$set": data})
        if result.matched_count == 0:
            logger.warning(f"Post to update not found: {post_id}")
            raise NotFoundError("Post not found")
        logger.info(f"Post updated: {post_id}")
        return result.modified_count
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating post: {e}")
        raise DatabaseException(str(e))


def delete_post(post_id):
    try:
        obj_id = ObjectId(post_id)
        result = collection.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            logger.warning(f"Post to delete not found: {post_id}")
            raise NotFoundError("Post not found")
        logger.info(f"Post deleted: {post_id}")
        return result.deleted_count
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        raise DatabaseException(str(e))


def get_all_posts():
    try:
        results = list(collection.find({}, {
            "_id": 1,
            "file_name": 1,
            "created_at": 1,
            "metadata": 1
        }))
        for r in results:
            r["_id"] = str(r["_id"])
        return results
    except Exception as e:
        logger.error(f"Failed to fetch all posts: {e}")
        raise DatabaseException(str(e))


def get_post_by_id(post_id):
    try:
        return collection.find_one({"_id": ObjectId(post_id)})
    except Exception as e:
        logger.error(f"Failed to get post by id: {e}")
        raise DatabaseException(str(e))


def save_graph_response(post_id, graph_data):
    try:
        obj_id = ObjectId(post_id)
        result = collection.update_one(
            {"_id": obj_id},
            {"$set": {"graph_response": graph_data}}
        )
        if result.matched_count == 0:
            logger.warning(f"Post not found when saving graph response: {post_id}")
            raise NotFoundError("Post not found")
        logger.info(f"Graph response saved for post: {post_id}")
        return result.modified_count
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to save graph response: {e}")
        raise DatabaseException(str(e))
