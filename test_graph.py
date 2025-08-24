from bpmn_neo4j.parsers.json_parser import load_json
from bpmn_neo4j.validators.schema_validator import validate_schema
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

# 1. Load JSON (make sure you have a sample BPMN JSON file)
data = load_json("output_bpmn (1).json")

# 2. Validate Schema (auto-fix common issues if enabled)
validated = validate_schema(data, auto_fix=True)

# 3. Validate BPMN Semantics
validate_semantics(validated)

# 4. Transform into Cypher queries
transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()

# 5. Save the queries to a .cql file (so you can run them manually in Neo4j Browser)
output_file = "output_queries.cql"
transformer.write_to_file(output_file)
print(f"✅ Cypher queries saved to {output_file}")

# 6. (Optional) Print queries directly in the terminal
print("\n=== Generated Cypher Queries ===")
for q in cypher_lines:
    print(q)

