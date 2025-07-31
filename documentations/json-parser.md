# 📚 JSON Parser Utility Documentation

## 🔍 Overview

This module provides a robust JSON loader that can automatically repair malformed JSON files using multiple fallback strategies. It's designed for use cases where incoming JSON files may not conform to strict standards but still contain structurally useful information.

## 🎯 Purpose

The purpose of this utility is to load a JSON file as Python data safely. If the file is malformed (e.g., due to extra commas, unquoted keys, etc.), it attempts to auto-repair the structure using multiple strategies.

## 📂 Location

```
app/
└── core/
    └── parsers/
        └── json_parser.py
```

## 🚀 Features

- Automatically repairs broken JSON using:
  - dirtyjson
  - demjson3
  - a custom heuristic method
- Installs missing packages on-the-fly
- Saves repaired versions of JSON files with clear suffixes
- Falls back to minimal structure if all repair attempts fail

## 💻 Usage

```python
from app.core.parsers.json_parser import load_json

data = load_json("path/to/your/file.json")
```

If the JSON is broken, a repaired version will be saved as:

```
file_fixed_by_<method>.json
```

## 🧭 Repair Strategy Order

1. Standard `json.loads`
2. `dirtyjson`
3. `demjson3`
4. Custom `heuristic_repair`
5. Fallback default BPMN structure

## 🧩 Functions

### load_json(path)

Attempts to load a JSON file with progressive fallback repairs.

- **Parameter**: `path` *(str)* – Path to the target JSON file  
- **Returns**: `dict` – Parsed JSON object or fallback structure

### heuristic_repair(raw_text)

Performs line-by-line analysis and adds:
- Missing commas between key-value pairs
- Missing closing brackets (`}` or `]`)

- **Parameter**: `raw_text` *(str)* – The original JSON content as a string  
- **Returns**: `str` – Repaired JSON string

### save_fixed_json(data, original_path, method="")

Saves a repaired JSON dictionary into a new file.

- **Parameters**:
  - `data` *(dict)* – Repaired JSON data  
  - `original_path` *(str)* – Original file path  
  - `method` *(str)* – The name of the repair method used (e.g. `"dirtyjson"`)

## ⚠️ Error Handling

Each repair strategy is wrapped in try-except blocks. When an error occurs, the module:
- Logs the error
- Attempts the next strategy
- Shows the method used (or fallback used) via terminal logs

Example log output:

```
❌ Standard JSON parsing failed
🛠️ Attempting to repair using dirtyjson...
✅ JSON repaired using dirtyjson.
```

## 📦 Dependencies

If repair is needed, the following Python libraries will be imported or installed automatically:

- [`dirtyjson`](https://pypi.org/project/dirtyjson/)
- [`demjson3`](https://pypi.org/project/demjson3/)

If not installed, the module will attempt:

```python
subprocess.check_call([sys.executable, "-m", "pip", "install", "dirtyjson"])
```

