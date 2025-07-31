# 📁 `data/` Folder Documentation

This directory contains **parsed BPMN JSON files** that are ready to be processed by the pipeline.

---

## 🧠 Purpose

Each JSON file in this folder represents a BPMN diagram that has already passed through initial parsing and structural validation.

These files are intermediate representations used as input for the BPMN transformation and validation pipeline.

---

## 🧩 Usage

The files are typically consumed by the **pipeline runner** script on `dev_run_pipeline.py` , which takes them as input and produces graph-compatible Cypher queries.

> For details on running the pipeline, refer to the `run-pipeline.md` documentation.

---

## 📤 Output

Using a file from this folder as input will result in:
- A `.cypher` file containing graph creation statements (usually in `output/`)
- Optional validation results depending on implementation

---

## 🧼 Maintenance

- File names are timestamped to help track versions.
- It is recommended to clean up unused or outdated files regularly to reduce clutter.

