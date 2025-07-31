# 📚 BPMN Services Documentation

## 🔍 Overview

The `bpmn_services.py` module defines a high-level orchestration function `run_bpmn_pipeline` that validates a BPMN JSON file, transforms it into Cypher statements, saves the statements to a file, and executes them on a Neo4j database.

This function ties together multiple components of the BPMN system such as schema validation, semantic validation, graph transformation, and Neo4j execution.

## 📂 Location

```
app/
└── core/
    └── services/
        └── bpmn_services.py
```

---

## 🧩 Function: `run_bpmn_pipeline(...)`

### Purpose

To run a complete BPMN-to-graph pipeline in a single function call, performing:

- JSON loading
- Schema validation
- Semantic validation
- Graph transformation to Cypher
- Cypher export to file
- Cypher execution on Neo4j

---

### 📥 Parameters

| Name               | Type   | Default              | Description                                      |
|--------------------|--------|----------------------|--------------------------------------------------|
| `input_json_path`  | str    | —                    | Path to the BPMN JSON input file                 |
| `output_cypher_path`| str   | —                    | File path where Cypher output will be written   |
| `neo4j_uri`        | str    | `bolt://localhost:7687` | Neo4j connection URI                        |
| `neo4j_user`       | str    | `neo4j`              | Username for Neo4j connection                    |
| `neo4j_password`   | str    | `12345678`           | Password for Neo4j connection                    |
| `reset_db`         | bool   | `True`               | Whether to clear the Neo4j database before import |

---

### 🔧 Process Flow

1. **Load JSON**
   ```python
   data = load_json(input_json_path)
   ```

2. **Schema Validation**
   - Uses `validate_schema(data, auto_fix=True)` to check structure
   - Attempts to auto-repair schema issues

3. **Semantic Validation**
   - Uses `validate_semantics(data)` to ensure logical BPMN correctness

4. **Graph Transformation**
   - `GraphTransformer` converts JSON into Cypher query list

5. **Save Cypher File**
   - Writes the generated Cypher to `output_cypher_path`

6. **Neo4j Execution**
   - Connects to Neo4j
   - Runs `setup_indexes()` and `run_cypher_lines()` (in batch)

---

### 📤 Example Usage

```python
run_bpmn_pipeline(
    input_json_path="input/process.json",
    output_cypher_path="output/process.cypher",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password123",
    reset_db=True
)
```

---

### ✅ Console Output Example

```
🔄 Loading JSON...
🔍 Validating JSON structure...
🧠 Validating BPMN logic...
🧱 Generating Cypher statements...
💾 Saving Cypher file...
🌐 Connecting to Neo4j...
🟢 Connection OK. Setting up indexes...
📤 Sending Cypher to Neo4j (batched)...
✅ BPMN pipeline complete.
```

---

## 🧷 Dependencies

This function relies on the following internal components:

- `load_json()` from `app.core.parsers.json_parser`
- `validate_schema()` from `validators.schema_validator`
- `validate_semantics()` from `validators.bpmn_semantic_validator`
- `GraphTransformer` from `app.core.transformers.graph_transformer`
- `Neo4jExecutor` from `app.core.repositories.neo4j_repositories`

---

## 📎 Notes

- It’s recommended to always pass `reset_db=True` on first run to ensure a clean Neo4j state
- The Cypher output is saved to disk for inspection or manual import if needed
- You should have a running Neo4j instance before executing this pipeline


