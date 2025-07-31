# 🧪 `validators/` Module Documentation

This module is responsible for **validating the structure and semantics** of BPMN JSON files before they are transformed into graph structures or executed into Neo4j.

---

## 📁 Files Overview

```
validators/
├── bpmn_schema.json
├── schema_validator.py
└── bpmn_semantic_validator.py
```

---

## 📄 `bpmn_schema.json`

Defines the **JSON Schema (Draft 07)** used for validating the structural integrity of BPMN JSON data. It ensures the existence and types of core BPMN elements:

- `activities` – Must contain valid task types (`userTask`, `manualTask`, etc.)
- `events` – Supports types like `startEvent`, `endEvent`, `boundaryEvent`
- `flows` – Must include valid `source`, `target`, and `type` (`sequence`, `message`)
- `gateways` – Validates exclusive/inclusive/parallel/etc.

Each object must have:
- A valid `id` (string)
- Required fields like `type`, `name`, `event_type`, or `gateway_type`

---

## 🧩 `schema_validator.py`

Provides structural validation logic for the BPMN JSON using the defined schema.

### 🔧 Main Function

```python
validate_schema(data, schema_path, auto_fix=False)
```

#### Tasks performed:
- Checks for missing root fields like `elements`, `activities`, `flows`
- Validates JSON structure using `jsonschema`
- Detects and fixes:
  - 🆔 Missing IDs
  - 🧬 Duplicate IDs
  - 🔁 Circular sequence flows
- Optional auto-fix mechanism:
  - Fills missing required fields using schema-aware logic
  - Applies basic corrections to malformed JSON

#### Supporting functions:
- `fix_missing_ids(data)`
- `fix_duplicate_ids(data)`
- `auto_fix_schema(data, schema)`
- `detect_cycle(flows)`

---

## 🧠 `bpmn_semantic_validator.py`

This module provides **comprehensive semantic validation** of BPMN elements after basic schema validation. It enforces both the **official BPMN standard rules** and the **Method and Style** guidelines.

Semantic validation ensures that:
- Nodes are correctly connected
- Events behave as expected
- Gateways have appropriate flows
- Message flow rules are respected
- Nodes follow best practices (naming, labeling, uniqueness)

---

### 🔧 Main Entry Point

```python
validate_semantics(bpmn_json: dict, strict: bool = False)
```

#### Parameters:
- `bpmn_json`: The JSON object (dict) representing the BPMN model.
- `strict`: If `True`, the function raises an error on any semantic violation.

#### Responsibilities:
- Build connectivity maps (`incoming`, `outgoing`)
- Check flow references and cross-pool flows
- Validate semantic rules for:
  - Events
  - Activities
  - Gateways
  - Message flows
  - Boundary events
  - Labels
- Print errors and warnings
- Optionally halt on error (`strict=True`)

---

### 🧪 Validation Stages & Rules

#### 1. **Flow Reference Integrity**
- Rule `[BPMN 0101, 0102]`: Source and target of each flow must exist.
- Rule `[BPMN 0202]`: Sequence flows must not cross pool boundaries.

#### 2. **Event Validation**
Performed by: `validate_events(events, incoming, outgoing)`

Rules include:
- `[0105]` Start event must not have incoming flow
- `[0109]` Start event must not use Error trigger
- `[0112]` Boundary event must have outgoing flow but no incoming
- `[0114, 0113]` Intermediate events must have proper flow direction
- `[01151, 01161, 01122]` Valid triggers only
- `[01106]` Only one start event per subprocess
- Style rules: labels, naming conventions

#### 3. **Activity Validation**
Performed by: `validate_activities(activities, incoming, outgoing)`

Rules include:
- Each task must have at least one incoming and one outgoing flow
- Label must be present and unique across the process
- Duplicate task names trigger warnings

#### 4. **Gateway Validation**
Performed by: `validate_gateways(gateways, incoming, outgoing, events)`

Rules include:
- Inclusive/Exclusive gateways must have ≥2 outgoing flows
- Parallel gateways must have ≥2 incoming or outgoing
- Event-based gateways must point to intermediateCatchEvents
- Gateways must not use message flows

#### 5. **Orphan Node Detection**
Performed by: `validate_orphan_nodes(...)`

Checks for:
- Any node not having both incoming and outgoing flows
- Typically indicates a modeling error or forgotten connection

#### 6. **Pool and Lane Assignment Check**
Performed by: `validate_pool_lane(...)`

Style validation:
- All elements must belong to a pool and lane
- Missing assignment will trigger warnings

#### 7. **Message Flow Validation**
Performed by: `validate_message_flows(...)`

Rules include:
- `[0301]` Message flows must go **across pools**
- `[0302]` Valid sources: `sendTask`, `intermediateThrowEvent`, etc.
- `[0303]` Valid targets: `receiveTask`, `startEvent`, etc.
- `[Style 0304]` Label must be present to indicate message name

#### 8. **Boundary Event Matching**
Performed by: `validate_boundary_event_matching(...)`

Rules include:
- Boundary event with `Error` or `Escalation` must match throw event
- `[01124, 01127]` Match required by `error_ref` or `escalation_ref`
- Style checks: boundary and throw event labels must match

#### 9. **Label Best Practices**
Performed by: `validate_event_labels(...)`

Style rules:
- `[01105]` Start event must have label
- `[01101]` Message start → label starts with "Receive ..."
- `[01102–01104]` Timer/Signal/Conditional start event must describe trigger
- `[0115]` Throwing intermediate → must have label
- `[0129]` End event → label describes end state

#### 10. **Conditional Sequence Flow Rules**
Performed by: `validate_conditional_sequence_flows(...)`

Rules:
- `[0203]` A flow cannot have condition if it’s the only outgoing
- `[0204]` A flow from `parallelGateway` must not have condition

#### 11. **Gateway Label Validation**
Performed by: `validate_gateway_labels(...)`

Style rules:
- `[0135]` Gateway with multiple unlabeled outputs → warning
- `[0136]` Single unlabeled output → soft warning

---

### 📊 Graph Connectivity Summary

At the end of validation, the tool reports the percentage of nodes that are connected (have either incoming or outgoing flows). This is a quick health indicator of the process model.

```plaintext
📊 Graph connectivity: 94.12% of nodes are connected.
```

---

### ❌ Error vs ⚠️ Warning

- ❌ **Errors** are BPMN violations and can break execution or logic
- ⚠️ **Warnings** are best-practice suggestions to improve maintainability or clarity

---

### 🔁 Internal Helpers

### `get_pool(elements, node_id)`
→ Finds pool_id associated with a given node.

### `validate_events(...)`, `validate_activities(...)`, etc.
→ All split into modular, testable, and reusable rule sets.

---

### ✅ Best Practices

- Always run semantic validation **after** schema validation
- Set `strict=True` for CI/CD enforcement
- Extend validator with custom rules via plug-in structure (e.g., task duration rules, label patterns)

---

### 🧪 Example Integration

```python
from validators.schema_validator import validate_schema
from validators.bpmn_semantic_validator import validate_semantics

data = validate_schema(load_json("my_bpmn.json"), auto_fix=True)
validate_semantics(data, strict=True)
```

## ✅ Example Usage in Pipeline

```python
from validators.schema_validator import validate_schema
from validators.bpmn_semantic_validator import validate_semantics

json_data = load_json("example.json")
json_data = validate_schema(json_data, auto_fix=True)
validate_semantics(json_data)
```

---

## 🚨 Output Behavior

- ❌ Errors are printed and can optionally raise exceptions if `strict=True`
- ⚠️ Warnings are style-related and help improve maintainability

---

## 🧼 Recommended Practices

- Use `auto_fix=True` for forgiving input validation
- Run both schema and semantic validation before transformation
- Extend schema as BPMN support expands

---

