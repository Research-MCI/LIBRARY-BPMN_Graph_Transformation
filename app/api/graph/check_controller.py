from flask import Blueprint, jsonify, request, current_app
from app.infrastructure.db.mongo_client import mongo
from app.utils.logger import get_logger

bp = Blueprint("check", __name__, url_prefix="/check")
logger = get_logger(__name__)

@bp.route("/health", methods=["GET"])
def health():
    try:
        # Ping DB untuk health check
        mongo.connect()
        mongo.client.admin.command("ping")
        db_status = "ok"
    except Exception as e:
        logger.error(f"/health DB check failed: {e}")
        db_status = "unavailable"
    return jsonify({
        "status": "ok",
        "db": db_status,
        "env": current_app.config.get("FLASK_ENV", "unknown"),
        "version": "1.0.0"
    })

@bp.route("/debug", methods=["GET"])
def debug():
    return jsonify({
        "headers": dict(request.headers),
        "remote_addr": request.remote_addr,
        "method": request.method,
        "args": request.args,
        "env": current_app.config.get("FLASK_ENV", "unknown"),
    })
