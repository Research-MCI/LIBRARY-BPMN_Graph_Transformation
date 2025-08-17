from bpmn_neo4j.parsers.json_parser import load_json
from bpmn_neo4j.validators.schema_validator import validate_schema
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
from bpmn_neo4j.neo4j.neo4j_repositories import Neo4jExecutor

# 1. Baca JSON (pastikan kamu punya file contoh)
data = load_json("output_bpmn (1).json")

# 2. Validasi Schema
validated = validate_schema(data, auto_fix=True)

# 3. Validasi Semantics
validate_semantics(validated)

# 4. Transformasi ke Cypher
transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()

# 5. Eksekusi ke Neo4j
executor = Neo4jExecutor("bolt://localhost:7687", "neo4j", "12345678")
executor.setup_indexes()
executor.run_batch(
    cypher_lines,
    reset=True,
    batch_size=20,
    process_id=transformer.process_id
)

# 6. Ambil Metrik
print(executor.get_metrics(transformer.process_id))

executor.close()
