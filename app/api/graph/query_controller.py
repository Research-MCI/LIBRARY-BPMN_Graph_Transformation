from flask import Blueprint, request
from app.core.services import post_service
from app.utils.logger import get_logger
from app.utils.exceptions.response import success_response, error_response
from app.core.services.query_service import QueryService

bp = Blueprint("query", __name__)
logger = get_logger(__name__)

@bp.route("/<post_id>/cypher", methods=["GET"])
def get_cypher_by_post(post_id):
    try:
        post = post_service.get_post_by_id(post_id)
        cypher_lines = post.get("cypher_full", [])
        return success_response(cypher_lines)
    except Exception as e:
        logger.error(f"Error fetching cypher for {post_id}: {e}", exc_info=True)
        return error_response("Failed to fetch cypher", code=500)

query_service = QueryService()

@bp.route("/<post_id>/cypher/response", methods=["GET"])
def get_cypher_response(post_id):
    try:
        result = query_service.get_graph_response_by_post_id(post_id)
        return success_response(result)
    except Exception as e:
        logger.error(f"Error generating graph response: {e}", exc_info=True)
        return error_response("Failed to generate graph response", code=500)