import os
from datetime import datetime, timezone

from app.core.parsers.json_parser import load_json
from validators.schema_validator import validate_schema
from validators.bpmn_semantic_validator import validate_semantics
from app.core.repositories.neo4j_repositories import Neo4jExecutor
from app.core.transformers.graph_transformer import GraphTransformer
from app.core.services import post_service
from app.utils.logger import get_logger


class BPMNGraphConverter:
    def __init__(self, config: dict = None):
        self.logger = get_logger()
        config = config or {}

        self.neo4j_uri = config.get("neo4j_uri", "bolt://localhost:7687")
        self.neo4j_user = config.get("neo4j_user", "neo4j")
        self.neo4j_password = config.get("neo4j_password", "12345678")
        self.reset_db = config.get("reset_db", True)
        self.batch_size = config.get("batch_size", 20)
        self.external_model_id = config.get("external_model_id")  # ⬅️ Ditambahkan

        self.logger.info(
            f"📦 Config: uri={self.neo4j_uri}, user={self.neo4j_user}, reset_db={self.reset_db}, batch_size={self.batch_size}, external_model_id={self.external_model_id}"
        )

    def convert_file(self, input_json_path: str, save_cypher_to: str = None, original_filename: str = None):
        self.logger.info(f"🔄 Loading JSON from {input_json_path}")
        data = load_json(input_json_path)

        self.logger.info("🔍 Validating structure...")
        data = validate_schema(data, auto_fix=True)

        self.logger.info("🧠 Validating semantics...")
        validate_semantics(data)

        self.logger.info("🧱 Transforming to graph...")
        transformer = GraphTransformer(json_data=data)
        cypher_lines = transformer.transform()
        process_id = transformer.process_id  # Ambil process_id dari transformer

        if save_cypher_to:
            self.logger.info(f"💾 Saving Cypher to {save_cypher_to}")
            os.makedirs(os.path.dirname(save_cypher_to), exist_ok=True)
            with open(save_cypher_to, "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in cypher_lines)

        self.logger.info("🌐 Connecting to Neo4j...")
        executor = Neo4jExecutor(uri=self.neo4j_uri, user=self.neo4j_user, password=self.neo4j_password)

        self.logger.info(f"🧾 Reset flag passed to executor: {self.reset_db}")

        if executor.run_health_check():
            self.logger.info("🟢 Connection OK. Setting up indexes...")
            executor.setup_indexes()

            self.logger.info("📤 Sending Cypher to Neo4j...")
            executor.run_batch(
                cypher_lines,
                reset=self.reset_db,
                batch_size=self.batch_size,
                process_id=process_id
            )

            graph_stats = executor.get_metrics(process_id)
            executor.close()
            self.logger.info("✅ Graph import complete.")

            # Simpan metadata ke MongoDB
            process_metadata = {
                "filename": original_filename or os.path.basename(input_json_path),
                "process_id": process_id,
                "node_count": transformer.node_count,
                "edge_count": transformer.edge_count,
                "graph_stats": graph_stats,
                "status": "imported",
                "created_at": datetime.now(timezone.utc),
                "cypher_full": cypher_lines,
                "raw_json": data,
                "source": "graph_converter"
            }

            if self.external_model_id:
                process_metadata["external_model_id"] = self.external_model_id

            self.logger.info("📥 Inserting metadata to MongoDB via post_service...")
            post_id = post_service.create_post(process_metadata, external_model_id=self.external_model_id)
            self.logger.info(f"✅ Metadata inserted with post_id: {post_id}")

            return {
                "message": "success",
                "post_id": post_id,
                "metadata": {
                    "filename": original_filename or os.path.basename(input_json_path),
                    "node_count": transformer.node_count,
                    "edge_count": transformer.edge_count,
                    "status": "imported",
                },
                "external_model_id": self.external_model_id  # untuk response jika fetch
            }

        else:
            raise ConnectionError("Neo4j is not reachable.")
