# BPMN → Neo4j Graph Transformation Library

A Python library for converting **BPMN Extension** into a **BPMN JSON** and nxt converting **BPMN JSON** into a **Neo4j graph database**.  
It provides parsing, schema validation, semantic validation, and transformation to Cypher.  

---

## 📂 Project Structure
```
project-root/
├── src/
    ├── bpmn-mp/
    │   ├── parsers/            # Extension parsing
    │   └── dispatcher/         # Dispatch Extension
    └── bpmn-neo4j-lib/
        ├── parsers/            # JSON parsing
        ├── validators/         # Schema + semantic validation
        ├── transformers/       # GraphTransformer, node/edge builders
        ├── utils/              # Logger
        └── exceptions/         # Custom error handling
```

---

## 📦 Installation

```bash
pip install bpmn-graph-transformation
```

### Requirements:
- Python 3.10+
- Neo4j 5.x (local or remote)

---

## 🚀 Usage

You can use the library step by step, or orchestrate the whole process with your own wrapper.

---

### 🔹 Step-by-step Example

#### 1. Load BPMN file
```python
import json
from bpmn_mp.dispatcher import dispatch_parse

def parse_and_save_bpmn(bpmn_path, output_path):
    result, _ = dispatch_parse(bpmn_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return result

data = parse_and_save_bpmn("examples/MyDiagram1.bpmn", "examples/sample_bpmn.json")
```

#### 2. Load a JSON file
```python
from bpmn_neo4j.parsers.json_parser import load_json

data = load_json("examples/sample_bpmn.json")
```
✅ Reads a BPMN JSON file.  
If the file is broken (invalid JSON), the parser attempts auto-repair and saves a `_fixed_by_<method>.json` file.

---

#### 3. Validate schema
```python
from bpmn_neo4j.validators.schema_validator import validate_schema

validated = validate_schema(data, auto_fix=True)
```
✅ Ensures JSON follows the official BPMN schema.  
`auto_fix=True` automatically assigns missing IDs, removes duplicates, and fills required fields.

---

#### 4. Validate semantics
```python
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics

validate_semantics(validated)
```
✅ Checks BPMN Method & Style rules:
- All flows have valid source/target.  
- Start/End events are consistent.  
- Activities and gateways follow BPMN rules.  
- Detects orphan nodes or invalid boundary/message flows.

---

#### 5. Transform JSON into Cypher
```python
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()
```
✅ Converts BPMN nodes & flows into Cypher queries:
- Creates nodes: Activities, Events, Pools, Lanes.  
- Creates edges: Sequence Flows.  
- Keeps track of process_id, node_count, and edge_count.  

---

#### 6. Save Cypher queries to file
```python
output_file = "output_queries.cql"
transformer.write_to_file(output_file)
print(f"✅ Cypher queries saved to {output_file}")
```
✅ Stores all generated Cypher queries in a .cql file that can be run directly in Neo4j Browser.

---

#### 7. (Optional) Print queries in the terminal
```python
for q in cypher_lines:
    print(q)
```

---

### 🔹 Output Example
```
CREATE (:Activity {id: "task_1", name: "Approve Invoice", process_id: "1234"})
CREATE (:Event {id: "start_1", type: "start", process_id: "1234"})
CREATE (:Event {id: "end_1", type: "end", process_id: "1234"})
CREATE (a1)-[:SEQUENCE_FLOW {id: "flow_1"}]->(a2)
.......
```

---

### 🔹 Full Example
```python
import json
from bpmn_mp.dispatcher import dispatch_parse
from bpmn_neo4j.parsers.json_parser import load_json
from bpmn_neo4j.validators.schema_validator import validate_schema
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

# 1. Parse BPMN and save as JSON
def parse_and_save_bpmn(bpmn_path, output_path):
    result, _ = dispatch_parse(bpmn_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return result

# Set your input/output file paths
bpmn_file = "examples/MyDiagram1.bpmn"
json_file = "examples/sample_bpmn.json"
cql_file = "examples/output_queries.cql"

# Parse BPMN and save to JSON
parse_and_save_bpmn(bpmn_file, json_file)

# 2. Load the generated JSON
data = load_json(json_file)

# 3. Validate Schema (auto-fix common issues if enabled)
validated = validate_schema(data, auto_fix=True)

# 4. Validate BPMN Semantics
validate_semantics(validated)

# 5. Transform into Cypher queries
transformer = GraphTransformer(json_data=validated)
cypher_lines = transformer.transform()

# 6. Save the queries to a .cql file
transformer.write_to_file(cql_file)
print(f"✅ Cypher queries saved to {cql_file}")

# 7. (Optional) Print queries directly in the terminal
print("\n=== Generated Cypher Queries ===")
for q in cypher_lines:
    print(q)
```

---

## 🧪 Running Tests
```bash
python test.py
```

