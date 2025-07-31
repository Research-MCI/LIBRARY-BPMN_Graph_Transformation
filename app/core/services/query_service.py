from app.core.repositories.post_repository import get_post_by_id, update_post
from app.core.repositories.neo4j_repositories import Neo4jExecutor
from app.core.transformers.graph_transformer import GraphTransformer

import os

neo4j_executor = Neo4jExecutor(
    uri=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "12345678")
)


class QueryService:
    def get_graph_response_by_post_id(self, post_id: str):
        post = get_post_by_id(post_id)

        if not post or "process_id" not in post:
            raise ValueError("Process ID tidak ditemukan pada post")

        process_id = post["process_id"]
        raw_data = neo4j_executor.fetch_graph_by_process_id(process_id)

        # ✅ Simpan hasilnya ke MongoDB
        update_post(post_id, {"graph_response": raw_data})

        return {"data": raw_data}

    
    def get_graph_visual_by_post_id(self, post_id: str):
        post = get_post_by_id(post_id)

        graph_response = post.get("graph_response", [])
        transformer = GraphTransformer(json_data={})  # json_data tidak dipakai
        visual_graph = transformer.visualize_graph_from_response(graph_response)

        # ✅ Simpan hasil visualisasi ke MongoDB
        update_post(post_id, {
            "graph_visual": visual_graph  # <-- disimpan terpisah
     })

        return visual_graph
