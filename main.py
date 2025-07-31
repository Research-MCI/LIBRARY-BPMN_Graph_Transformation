import os
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from app.infrastructure.config import get_config
from app.infrastructure.db.mongo_client import mongo
from app.utils.logger import get_logger
from app.api.graph.routes import register_routes

# --- Flask app factory ---

def create_app():
    config_cls = get_config()
    app = Flask(__name__)
    app.config.from_object(config_cls)
    
    # Logger setup
    logger = get_logger("app", app.config)
    logger.info(f"Starting Flask app in {app.config['FLASK_ENV'].upper()} mode")

    # Register Blueprints/routes
    register_routes(app)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.warning(f"HTTPException: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": e.description,
                    "code": e.code,
                }
            ),
            e.code,
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "code": 500,
                }
            ),
            500,
        )

    return app


# --- Gunicorn compatibility ---
# Gunicorn expects 'app' at global scope

app = create_app()

# --- Dev CLI runner ---
if __name__ == "__main__":
    # Flask dev server only (not for production)
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_RUN_PORT", 5050)),
        debug=app.config.get("DEBUG", False),
    )
