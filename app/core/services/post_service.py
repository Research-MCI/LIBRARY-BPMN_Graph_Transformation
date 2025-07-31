import os
from app.core.repositories import post_repository as repo
from app.core.schemas.post_schema import validate_post_input
from app.utils.exceptions.business_exceptions import ValidationError
from app.core.repositories.neo4j_repositories import Neo4jExecutor
from app.infrastructure.db.mongo_client import get_db


def create_post(data, external_model_id=None):
    if external_model_id:
        data["external_model_id"] = external_model_id

    is_valid, errors = validate_post_input(data)
    if not is_valid:
        raise ValidationError(str(errors))

    return repo.create_post(data)


def get_post(post_id):
    return repo.get_post(post_id)


def update_post(post_id, data):
    is_valid, errors = validate_post_input(data)
    if not is_valid:
        raise ValidationError(str(errors))
    return repo.update_post(post_id, data)


def delete_post(post_id):
    return repo.delete_post(post_id)


def get_all_posts():
    return repo.get_all_posts()


def get_post_analysis(post_id: str):
    post = repo.get_post(post_id)
    post["_id"] = str(post["_id"])
    
    file_name = post.get("filename")
    created_at = post.get("created_at")
    process_id = post.get("process_id")

    if not process_id:
        raise ValidationError("Process ID not found in post metadata")

    executor = Neo4jExecutor(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    graph_stats = executor.get_metrics(process_id)
    executor.close()

    return {
        "file_name": file_name,
        "created_at": created_at,
        "graph_stats": graph_stats,
    }


def compare_posts(ids: list):
    if not ids or len(ids) < 2:
        raise ValidationError("At least two process IDs are required for comparison.")

    results = []
    for post_id in ids:
        post = repo.get_post(post_id)
        results.append({
            "_id": str(post["_id"]),
            "file_name": post.get("file_name"),
            "metadata": post.get("metadata", {}),
            "graph_stats": post.get("graph_stats", {})
        })
    return results


def get_process_paths(post_id: str):
    post = repo.get_post(post_id)
    process_id = post.get("process_id")

    if not process_id:
        raise ValidationError("Process ID not found in post metadata")

    executor = Neo4jExecutor(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    paths = executor.find_paths(process_id)
    executor.close()
    return paths


def get_process_metrics(post_id: str):
    post = repo.get_post(post_id)
    process_id = post.get("process_id")

    executor = Neo4jExecutor(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    metrics = executor.get_metrics(process_id)
    executor.close()
    return metrics


def execute_cypher_query(query: str):
    executor = Neo4jExecutor(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    results = executor.run_custom_query(query)
    executor.close()
    return results


def get_post_by_id(post_id):
    return repo.get_post_by_id(post_id)


def check_health():
    # Check MongoDB
    mongo_ok = False
    try:
        db = get_db()
        db.list_collection_names()
        mongo_ok = True
    except Exception:
        mongo_ok = False

    # Check Neo4j
    try:
        executor = Neo4jExecutor(
            uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "12345678")
        )
        neo4j_ok = executor.run_health_check()
        executor.close()
    except Exception:
        neo4j_ok = False

    return {
        "mongo": mongo_ok,
        "neo4j": neo4j_ok
    }


def get_graph_response(post_id: str):
    post = repo.get_post_by_id(post_id)
    process_id = post.get("process_id")
    if not process_id:
        raise ValidationError("Process ID not found in post metadata")

    executor = Neo4jExecutor(
        uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "12345678")
    )
    raw_records = executor.fetch_graph_by_process_id(process_id)
    executor.close()

    repo.update_post(post_id, {"raw_graph": raw_records})

    return {"data": raw_records}
