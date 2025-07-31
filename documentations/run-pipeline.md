# 📄 dev_run_pipeline.py

This file is the **entrypoint script** used to test the BPMN validation and transformation pipeline locally.

---

## 🧪 Purpose

This script runs the full pipeline for a specific JSON file inside `data/` and writes the result into `output/output.cypher`.

---

## ⚙️ Usage

```bash
python dev_run_pipeline.py
```

This will load the following hardcoded input path:

```python
input_json_path='data/bpmn_parse_output_20250609_184311.json' #example
```

The corresponding Cypher output will be written to:

```python
output_cypher_path='output/output.cypher'
```

---

## 🛠️ Dependencies

- `app.core.services.bpmn_services.run_bpmn_pipeline`
- Input JSON file (e.g., `data/bpmn_parse_output_*.json`)
- Output directory: `output/`

---

## 🔁 Pipeline Flow

1. Load input BPMN JSON
2. Run schema validation
3. Run semantic validation
4. Generate Cypher output for Neo4j

---
