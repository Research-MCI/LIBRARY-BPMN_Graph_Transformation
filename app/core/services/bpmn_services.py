import os

from app.core.parsers.json_parser import load_json
from validators.schema_validator import validate_schema
from validators.bpmn_semantic_validator import validate_semantics
from app.core.repositories.neo4j_repositories import Neo4jExecutor
from app.core.transformers.graph_transformer import GraphTransformer


def run_bpmn_pipeline(
    input_json_path: str,
    output_cypher_path: str,
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "12345678",
    reset_db: bool = True
):
    print("\n🔄 Loading JSON...")
    data = load_json(input_json_path)

    print("🔍 Validating JSON structure...")
    data = validate_schema(data, auto_fix=True)

    print("🧠 Validating BPMN logic...")
    validate_semantics(data)

    print("🧱 Generating Cypher statements...")
    transformer = GraphTransformer(json_data=data)
    cypher_lines = transformer.transform()

    print("💾 Saving Cypher file...")
    os.makedirs(os.path.dirname(output_cypher_path), exist_ok=True)
    with open(output_cypher_path, 'w', encoding='utf-8') as f:
        for line in cypher_lines:
            f.write(line + '\n')

    print("🌐 Connecting to Neo4j...")
    executor = Neo4jExecutor(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)

    if executor.run_health_check():
        print("🟢 Connection OK. Setting up indexes...")
        executor.setup_indexes()

        print("📤 Sending Cypher to Neo4j (batched)...")
        executor.run_cypher_lines(cypher_lines, reset=reset_db, batch_size=20)
    else:
        print("❌ Neo4j is not reachable. Aborting.")

    executor.close()
    print("✅ BPMN pipeline complete.")
