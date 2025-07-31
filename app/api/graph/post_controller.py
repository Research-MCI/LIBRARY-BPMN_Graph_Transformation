from flask import Blueprint, request
from app.core.services import post_service
from app.utils.logger import get_logger
from app.utils.exceptions.response import success_response, error_response
from app.utils.exceptions.db_exceptions import DatabaseException, NotFoundError
from app.utils.exceptions.business_exceptions import ValidationError

bp = Blueprint("posts", __name__, url_prefix="/posts")
logger = get_logger(__name__)

@bp.route("/", methods=["POST"])
def create():
    try:
        data = request.json
        post_id = post_service.create_post(data)
        logger.info(f"API: Post created with id {post_id}")
        return success_response({"id": post_id}, message="Created", code=201)
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        return error_response(str(ve), code=422)
    except DatabaseException as de:
        logger.error(f"Database error: {de}")
        return error_response(str(de), code=500)
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return error_response(str(e), code=500)

@bp.route("/<post_id>", methods=["GET"])
def read(post_id):
    try:
        result = post_service.get_post(post_id)
        result["_id"] = str(result["_id"])
        return success_response(result)
    except NotFoundError as nf:
        logger.warning(f"Read: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Read: Unknown error: {e}")
        return error_response(str(e), code=500)

@bp.route("/<post_id>", methods=["PUT"])
def update(post_id):
    try:
        data = request.json
        post_service.update_post(post_id, data)
        return success_response(message="Updated")
    except ValidationError as ve:
        logger.warning(f"Update validation error: {ve}")
        return error_response(str(ve), code=422)
    except NotFoundError as nf:
        logger.warning(f"Update not found: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Update: Unknown error: {e}")
        return error_response(str(e), code=500)

@bp.route("/<post_id>", methods=["DELETE"])
def delete(post_id):
    try:
        post_service.delete_post(post_id)
        return success_response(message="Deleted")
    except NotFoundError as nf:
        logger.warning(f"Delete not found: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Delete: Unknown error: {e}")
        return error_response(str(e), code=500)

@bp.route("/<post_id>/metrics", methods=["GET"])
def get_metrics(post_id):
    try:
        metrics = post_service.get_process_metrics(post_id)
        return success_response(metrics)
    except NotFoundError as nf:
        logger.warning(f"Metrics: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Metrics error: {e}", exc_info=True)
        return error_response("Internal server error", code=500)