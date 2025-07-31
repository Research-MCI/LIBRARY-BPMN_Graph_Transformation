# app/api/v1/bpmn_controller.py

from flask import Blueprint, request
from werkzeug.utils import secure_filename
from app.core.libraries.graph_converter import BPMNGraphConverter
from app.utils.logger import get_logger
from app.utils.exceptions.response import success_response, error_response
from app.core.services import post_service
from app.utils.exceptions.db_exceptions import NotFoundError
from app.utils.exceptions.business_exceptions import ValidationError


import os
import tempfile
import uuid
import requests
import json


bp = Blueprint("bpmn", __name__)
logger = get_logger(__name__)

from bson import ObjectId

def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    else:
        return obj

@bp.route("/upload", methods=["POST"])
def upload_and_convert():
    try:
        if "upload" not in request.files:
            logger.warning("No 'upload' part in request.files")
            return error_response("No file part in the request", code=400)

        file = request.files["upload"]
        if file.filename == "":
            logger.warning("Empty filename")
            return error_response("No selected file", code=400)

        if not file.filename.endswith(".json"):
            logger.warning(f"Invalid file extension: {file.filename}")
            return error_response("Only .json BPMN files are supported", code=400)

        # Debug: print file content
        raw_content = file.read()
        logger.debug(f"Uploaded file content (first 500 bytes):\n{raw_content[:500]}")
        file.seek(0)  # reset pointer so it can be saved

        # Simpan file ke folder temporary
        temp_dir = tempfile.gettempdir()
        filename = secure_filename(file.filename)  # ➜ original filename
        unique_filename = f"{uuid.uuid4()}_{filename}"  # ➜ for saving only
        file_path = os.path.join(temp_dir, unique_filename)
        file.save(file_path)


        # Jalankan konversi
        converter = BPMNGraphConverter(config={
            "neo4j_uri": "bolt://neo4j:7687",
            "neo4j_user": "neo4j",
            "neo4j_password": "12345678",
            "reset_db": True,
        })

        result = converter.convert_file(file_path, original_filename=filename)

        cleaned_metadata = convert_objectid(result.get("metadata"))
        return success_response(
            message="BPMN file uploaded and processed successfully",
            data={
                "post_id": str(result.get("post_id")),
                "metadata": cleaned_metadata,
                "filename": filename
            }
        )

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        logger.error(f"Error processing uploaded BPMN file: {e}\n{traceback_str}")
        return error_response("Internal server error during upload", code=500)


@bp.route("/", methods=["GET"])
def list_all():
    try:
        posts = post_service.get_all_posts()
        return success_response(posts)
    except Exception as e:
        logger.error(f"List all processes failed: {e}")
        return error_response("Internal server error", code=500)
    

@bp.route("/<post_id>/analyze", methods=["GET"])
def analyze_process(post_id):
    try:
        result = post_service.get_post_analysis(post_id)
        return success_response(result)
    except NotFoundError as nf:
        logger.warning(f"Analyze: Not found {post_id}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Analyze error: {e}", exc_info=True)
        return error_response("Internal server error", code=500)
    
@bp.route("/compare", methods=["POST"])
def compare_processes():
    try:
        data = request.get_json()
        ids = data.get("ids", [])

        result = post_service.compare_posts(ids)
        return success_response(result)

    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        return error_response(str(ve), code=422)
    except NotFoundError as nf:
        logger.warning(f"Process not found: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Comparison failed: {e}", exc_info=True)
        return error_response("Internal server error", code=500)

@bp.route("/<post_id>/paths", methods=["GET"])
def get_paths(post_id):
    try:
        paths = post_service.get_process_paths(post_id)
        return success_response(paths)
    except NotFoundError as nf:
        logger.warning(f"Paths not found: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Error fetching paths: {e}", exc_info=True)
        return error_response("Internal server error", code=500)

@bp.route("/<post_id>/metrics", methods=["GET"])
def get_metrics(post_id):
    try:
        metrics = post_service.get_process_metrics(post_id)
        return success_response(metrics)
    except NotFoundError as nf:
        logger.warning(f"Metrics not found: {nf}")
        return error_response(str(nf), code=404)
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        return error_response("Internal server error", code=500)

@bp.route("/<post_id>/rawjson", methods=["GET"])
def get_raw_json(post_id):
    try:
        post = post_service.get_post(post_id)
        raw_json = post.get("raw_json")

        if not raw_json:
            logger.warning(f"Raw JSON not found for post_id: {post_id}")
            return error_response("Raw JSON not found", code=404)

        return success_response(raw_json)

    except NotFoundError:
        logger.warning(f"Post not found: {post_id}")
        return error_response("Post not found", code=404)
    except Exception as e:
        logger.error(f"Error fetching raw JSON: {e}", exc_info=True)
        return error_response("Internal server error", code=500)

@bp.route("/<post_id>/visual", methods=["GET"])
def get_visual_graph(post_id):
    try:
        from app.core.services.query_service import QueryService
        query_service = QueryService()

        result = query_service.get_graph_visual_by_post_id(post_id)
        return success_response(result)
    except Exception as e:
        logger.error(f"Visual graph error: {e}", exc_info=True)
        return error_response("Internal server error", code=500)

@bp.route("/fetch-and-convert/<model_id>", methods=["POST"])
def fetch_and_convert(model_id):
    try:
        base_url = os.getenv("URL_SERVER_MP", "http://10.21.83.106:3142")  
        external_url = f"{base_url}/api/v1/parse/{model_id}/result"
        response = requests.get(external_url)

        if response.status_code != 200:
            logger.warning(f"Failed to fetch JSON from external API for model_id: {model_id}")
            return error_response("Failed to fetch BPMN JSON from parser API", code=404)

        json_data = response.json()

        if "result" in json_data and isinstance(json_data["result"], dict):
            logger.info("📦 Detected nested 'result' field in JSON → extracting it for normalization")
            json_data = json_data["result"]

        temp_dir = tempfile.gettempdir()
        temp_filename = f"{uuid.uuid4()}_fetched_bpmn.json"
        file_path = os.path.join(temp_dir, temp_filename)

        with open(file_path, "w") as f:
            json.dump(json_data, f)

        converter = BPMNGraphConverter(config={
            "neo4j_uri": "bolt://neo4j:7687",
            "neo4j_user": "neo4j",
            "neo4j_password": "12345678",
            "reset_db": True,
            "external_model_id": model_id
        })

        result = converter.convert_file(file_path, original_filename=temp_filename)

        cleaned_metadata = convert_objectid(result.get("metadata"))

        return success_response(
            message="Successfully fetched, converted, and stored BPMN from external API",
            data={
                "post_id": str(result.get("post_id")),
                "metadata": cleaned_metadata,
                "filename": temp_filename,
                "external_model_id": result.get("external_model_id")
            }
        )

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        logger.error(f"Error during fetch-and-convert: {e}\n{traceback_str}")
        return error_response("Internal server error during fetch-and-convert", code=500)