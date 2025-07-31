from app.core.libraries.graph_converter import BPMNGraphConverter

converter = BPMNGraphConverter(config={
    "neo4j_uri": "bolt://localhost:7687",
    "neo4j_user": "neo4j",
    "neo4j_password": "12345678"
})
result = converter.convert_file("data/bpmn_parse_output_20250602_164152.json", save_cypher_to="output/output.cypher")
print(result)
