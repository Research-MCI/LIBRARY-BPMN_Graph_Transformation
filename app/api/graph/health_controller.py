from flask import Blueprint, jsonify, current_app
from app.infrastructure.db.mongo_client import mongo
from app.utils.logger import get_logger
from app.core.services import post_service

bp = Blueprint("health", __name__)
logger = get_logger(__name__)

@bp.route("/health", methods=["GET"])
def health():
    try:
        health = post_service.check_health()
        status = "ok" if health["mongo"] and health["neo4j"] else "partial"
        return jsonify({
            "status": status,
            "db": "ok" if health["mongo"] else "unavailable",
            "neo4j": "ok" if health["neo4j"] else "unavailable",
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"/health check failed: {e}")
        return jsonify({
            "status": "fail",
            "error": str(e)
        }), 500
