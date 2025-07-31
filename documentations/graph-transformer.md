# 🔄 Graph Transformer Module

This module is responsible for converting valid BPMN JSON structures into **Cypher queries** that can be executed in a Neo4j graph database. It bridges the gap between semantic BPMN definitions and executable graph structures.

## 📁 Location

```
app/core/transformers/
├── __init__.py
├── graph_transformer.py
├── edges.py
├── nodes.py
└── pool_lanes.py
```

---

## 🧠 Purpose

After parsing and validating a BPMN JSON file, this module takes over to:

- Interpret structural components (Pools, Lanes, Activities, Events, Gateways, Flows)
- Convert them into Cypher `CREATE` or `MATCH` queries
- Prepare graph-representable outputs suitable for execution in Neo4j

---

## ⚙️ Architecture and Flow

The transformation follows this **3-stage sequence**:

1. **Pools & Lanes**
2. **Nodes** (Activities, Events, Gateways)
3. **Edges** (Sequence Flows, Message Flows)

The output is a list of **Cypher queries** that can be:

- Written to a `.cypher` file
- Executed directly on a Neo4j instance via the `Neo4jExecutor`

---

## 📘 `graph_transformer.py`

Main class: `GraphTransformer`

### Constructor

```python
GraphTransformer(json_data: dict)
```

- Accepts parsed and validated BPMN JSON.
- Initializes internal buffers and logs.

### `transform() -> List[str]`

- Main method to perform full transformation.
- Calls sub-transformers in this order:
  - `process_pools_and_lanes`
  - `process_nodes`
  - `process_edges`

- Returns:
  - A flat list of Cypher query strings.

### Other Methods

- `write_to_file(path: str)`  
  Writes generated Cypher queries to a file.

- `batch_output(batch_size: int = 20)`  
  Yields queries in chunks, suitable for Neo4j bulk import.

- `execute_on_neo4j(executor: Neo4jExecutor)`  
  Sends Cypher queries directly to a connected Neo4j instance.

---

## 🧩 `pool_lanes.py`

Handles Pools and Lanes defined in the BPMN process.

### Pool Transformation

For each pool:
```cypher
CREATE (:Pool {id: ..., name: ..., type: ..., process_ref: ...});
```

### Lane Transformation

For each lane:
```cypher
CREATE (:Lane {id: ..., name: ..., pool_id: ..., lane_id: ...});
MATCH (l:Lane {id: ...}), (p:Pool {id: ...}) CREATE (l)-[:BELONGS_TO]->(p);
```

- Ensures each lane is connected to its parent pool via `BELONGS_TO`.

---

## 🔘 `nodes.py`

Generates node declarations in Cypher for:

### Activities

- Types: `task`, `userTask`, `scriptTask`, `serviceTask`, etc.

```cypher
CREATE (:Activity {id: ..., name: ..., type: ..., pool_id: ..., lane_id: ...});
```

### Events

- Types: `startEvent`, `endEvent`, `intermediateCatchEvent`, etc.

```cypher
CREATE (:Event {id: ..., name: ..., type: ..., event_type: ..., pool_id: ..., lane_id: ...});
```

### Gateways

- Types: `exclusiveGateway`, `inclusiveGateway`, `parallelGateway`

```cypher
CREATE (:Gateway {id: ..., name: ..., gateway_type: ..., pool_id: ..., lane_id: ...});
```

### Default Naming

- If an element has no `name`, fallback values like `"Unnamed Task"` or `"Start"` are used to avoid breaking the graph.

---

## 🔗 `edges.py`

Builds Cypher relationships based on:

- **Sequence Flows**
- **Message Flows**
- **Associations** (future support)

### General Structure

```cypher
MATCH (a {id: "source_id"}), (b {id: "target_id"})
CREATE (a)-[:SEQUENCE_FLOW {id: ..., label: ..., type: ...}]->(b);
```

### Flow Labeling

- Uses explicit `label` if present.
- Fallback to gateway type or `"SEQUENCE_FLOW"` if undefined.

### Relationship Types

- `SEQUENCE_FLOW`: Default transition between process elements.
- `MESSAGE_FLOW`: Cross-pool communication.
- `CONDITIONAL_FLOW` (if `conditionExpression` exists – future support)

---

## 📤 Example Output

```cypher
CREATE (:Pool {id: "pool_1", name: "Main Process"});
CREATE (:Lane {id: "lane_1", name: "Approval Lane"});
CREATE (:Activity {id: "task_approve", name: "Approve Request"});
MATCH (a {id: "start"}), (b {id: "task_approve"})
CREATE (a)-[:SEQUENCE_FLOW {id: "flow1"}]->(b);
```

---

## 🧪 Sample Usage

```python
from app.core.transformers.graph_transformer import GraphTransformer
from app.core.repositories.neo4j_repositories import Neo4jExecutor

transformer = GraphTransformer(json_data=bpmn_json)
cypher_lines = transformer.transform()

# Save to file
transformer.write_to_file("output/cypher_output.cypher")

# Execute on Neo4j
executor = Neo4jExecutor(uri="bolt://localhost:7687", user="neo4j", password="12345678")
transformer.execute_on_neo4j(executor)
```

---

## 📎 Notes

- Element IDs are assumed to be unique
- Relationships use `MATCH` to prevent node duplication
- Future expansion may include:
  - Conditional flows
  - Annotation associations
  - Error boundary events

---

## 📦 Dependencies

- `neo4j`
- `GraphTransformer`, `Neo4jExecutor`, and the core BPMN domain structure

---
