# BPMN → Neo4j Graph Transformation Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **📌 Note**: This is the official public repository for the BPMN Graph Transformation Library. Changes pushed to GitHub are automatically synchronized to our internal GitLab server at [https://gitlab.iimlab.id/business-process/LIBRARY-BPMN_Graph_Transformation](https://gitlab.iimlab.id/business-process/LIBRARY-BPMN_Graph_Transformation) for CI/CD pipelines (automated testing, PyPI publishing, and deployment).

---

## 📖 About

A Python library for transforming **BPMN (Business Process Model and Notation)** models into **Neo4j graph databases**. 

**Core Capabilities:**
- Parse multiple BPMN formats (BPMN 2.0 XML, XPDL, Bizagi native .bpm)
- Validate BPMN structure and semantics
- Generate Cypher queries for Neo4j graph creation
- Preserve pools, lanes, and message flows

---

## 🎯 Key Features

✅ **Multi-format parsing** - Supports BPMN 2.0 XML (.bpmn), XPDL 2.2 (.xpdl), Bizagi native (.bpm)  
✅ **Automatic format detection** - Plugin-based dispatcher automatically detects file format  
✅ **JSON repair** - Auto-fixes broken BPMN JSON using dirtyjson and demjson3  
✅ **Schema validation** - Validates against BPMN 2.0 structure with auto-fix capabilities  
✅ **Semantic validation** - Validates BPMN rules (events, gateways, flows, pools/lanes)  
✅ **Graph transformation** - Converts BPMN elements to Neo4j Cypher queries  
✅ **Pool & Lane preservation** - Maintains organizational structure in graph  
✅ **Message flow handling** - Supports cross-pool communication  

---

## 📦 Installation

### From PyPI (when published)
```bash
pip install bpmn-graph-transformation
```

### From Source
```bash
# Clone from GitHub (official public repository)
git clone https://github.com/YOUR_USERNAME/LIBRARY-BPMN_Graph_Transformation.git
cd LIBRARY-BPMN_Graph_Transformation

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Requirements
- Python 3.8+
- Neo4j 5.x (for executing generated Cypher queries)

---

## 🚀 Quick Start

### Example 1: Parse BPMN File
```python
import json
from bpmn_mp.dispatcher import dispatch_parse

# Automatically detects format (.bpmn, .xpdl, .bpm)
result, format_type = dispatch_parse("examples/MyDiagram1.bpmn")

# Save to JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ Parsed as {format_type} format")
```

### Example 2: Validate BPMN
```python
from bpmn_neo4j.parsers.json_parser import load_json
from bpmn_neo4j.validators.schema_validator import validate_schema
from bpmn_neo4j.validators.bpmn_semantic_validator import validate_semantics

# Load JSON (with auto-repair if needed)
data = load_json("output.json")

# Validate structure
validated = validate_schema(data, auto_fix=True)

# Validate BPMN semantics
validate_semantics(validated)
```

### Example 3: Transform to Neo4j
```python
from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

# Transform to Cypher queries
transformer = GraphTransformer(json_data=validated)
cypher_queries = transformer.transform()

# Save queries to file
transformer.write_to_file("output_queries.cql")

# Or print directly
for query in cypher_queries:
    print(query)
```

### Example 4: Execute in Neo4j
```bash
# Option 1: Neo4j Browser
# Open Neo4j Browser and paste queries from output_queries.cql

# Option 2: cypher-shell
cypher-shell -u neo4j -p password < output_queries.cql
```

---

## 📂 Project Structure

```
├── src/
│   ├── bpmn_mp/                    # Multi-format BPMN parser
│   │   ├── parsers/
│   │   │   ├── bpmn_parser/        # BPMN 2.0 XML parser
│   │   │   ├── xpdl_parser/        # XPDL 2.2 parser
│   │   │   ├── native_parser/      # Bizagi .bpm parser
│   │   │   └── xml_parser/         # Generic XML parser
│   │   └── dispatcher.py           # Auto-detect parser
│   │
│   └── bpmn_neo4j/                 # Neo4j transformation
│       ├── parsers/                # JSON parsing & repair
│       │   ├── json_parser.py      # JSON loader with auto-repair
│       │   └── parser_factory.py   # Parser factory
│       │
│       ├── validators/             # Validation modules
│       │   ├── schema_validator.py        # BPMN schema validation
│       │   ├── bpmn_semantic_validator.py # BPMN semantic rules
│       │   └── bpmn_schema.json          # JSON schema definition
│       │
│       ├── transformers/           # Neo4j transformation
│       │   ├── graph_transformer.py       # Main transformer
│       │   ├── nodes.py                   # Node generation
│       │   ├── edges.py                   # Edge generation
│       │   ├── pool_lanes.py              # Pool/lane generation
│       │   └── transform_input_elements.py # Input normalization
│       │
│       └── utils/                  # Utilities
│           └── logger.py           # Logging utilities
│
├── examples/                       # Sample BPMN files
├── tests/                          # Unit tests
├── LICENSE                         # MIT License
├── README.md                       # This file
└── pyproject.toml                  # Package configuration
```

---

## 🔬 Validation Features

### Schema Validation
The library validates BPMN JSON structure and can automatically fix common issues:

- ✅ **Missing IDs** - Auto-generates unique IDs for elements without them
- ✅ **Duplicate IDs** - Renames duplicate IDs with suffixes
- ✅ **Missing required fields** - Adds default values for required properties
- ✅ **Type compliance** - Validates element types against BPMN 2.0 spec
- ✅ **Circular dependencies** - Detects cycles in sequence flows

### Semantic Validation
Validates BPMN method and style rules including:

**Event Rules:**
- Start events cannot have incoming flows (BPMN 0105)
- End events cannot have outgoing flows (BPMN 0124)
- Intermediate throw events must have outgoing flows (BPMN 0114)
- Intermediate catch events must have incoming flows (BPMN 0113)

**Activity Rules:**
- Activities should have incoming flows (BPMN 0101)
- Activities should have outgoing flows (BPMN 0102)
- Activities should be labeled (Style 0103)

**Gateway Rules:**
- Exclusive/inclusive gateways should have ≥2 outgoing flows (BPMN 0134)
- Parallel gateways should have ≥2 incoming or outgoing flows (BPMN 0134)
- Event-based gateways must connect to intermediate catch events (BPMN 0138)

**Flow Rules:**
- Sequence flows must have valid source and target (BPMN 0101/0102)
- Sequence flows cannot cross pool boundaries (BPMN 0202)
- Message flows must cross pool boundaries (BPMN 0301)

**Pool/Lane Rules:**
- Orphan nodes detection
- Pool/lane assignment warnings

---

## 🗂️ Supported BPMN Elements

### Activities
- Task, User Task, Service Task, Send Task, Receive Task
- Manual Task, Business Rule Task, Script Task
- Call Activity, Subprocess

### Events
- Start Event (None, Message, Timer, Signal, Conditional, Multiple, Parallel Multiple)
- End Event (None, Message, Error, Escalation, Cancel, Compensation, Signal, Terminate, Multiple)
- Intermediate Catch Event (Message, Timer, Signal, Link, Conditional)
- Intermediate Throw Event (Message, Signal, Escalation, Link, Compensation)

### Gateways
- Exclusive Gateway
- Parallel Gateway
- Inclusive Gateway
- Event-Based Gateway
- Complex Gateway

### Flows
- Sequence Flow
- Message Flow

### Other Elements
- Pools
- Lanes

---

## 📝 Example Output

### Input: BPMN Process
```xml
<bpmn:startEvent id="start_1" name="Start"/>
<bpmn:task id="task_1" name="Process Invoice"/>
<bpmn:endEvent id="end_1" name="End"/>
<bpmn:sequenceFlow id="flow_1" sourceRef="start_1" targetRef="task_1"/>
<bpmn:sequenceFlow id="flow_2" sourceRef="task_1" targetRef="end_1"/>
```

### Output: Neo4j Cypher
```cypher
CREATE (e:Event {id: 'start_1', name: 'Start', type: 'startevent', 
  event_type: 'nonestart', process_id: 'abc123'});

CREATE (a:Activity {id: 'task_1', name: 'Process Invoice', type: 'task', 
  process_id: 'abc123'});

CREATE (e:Event {id: 'end_1', name: 'End', type: 'endevent', 
  event_type: 'noneend', process_id: 'abc123'});

MATCH (a {id: 'start_1'}) WITH a MATCH (b {id: 'task_1'}) 
CREATE (a)-[:SEQUENCE_FLOW {id: 'flow_1', name: 'flow 1'}]->(b);

MATCH (a {id: 'task_1'}) WITH a MATCH (b {id: 'end_1'}) 
CREATE (a)-[:SEQUENCE_FLOW {id: 'flow_2', name: 'flow 2'}]->(b);
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
python test_graph.py
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** this repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/
   ```
3. **Create** a feature branch
   ```bash
   git checkout -b feature/YourFeature
   ```
4. **Make** your changes and commit
   ```bash
   git commit -m 'Add: YourFeature'
   ```
5. **Push** to your fork
   ```bash
   git push origin feature/YourFeature
   ```
6. **Open** a Pull Request on GitHub

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📖 Citation

If you use this library in academic research, please cite:

```bibtex

```

**Citation information will be updated after publication.**

---

## 🏆 Acknowledgments

- Institut Teknologi Sepuluh Nopember (ITS)
- IIM Lab Research Team (Lab Manajemen Cerdas InformasI)

---

## 📬 Contact & Support

- **GitHub Repository**: [https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Research-MCI/LIBRARY-BPMN_Graph_Transformation/discussions)
- **Email**: 6025241065@student.its.ac.id
- **Internal CI/CD**: Changes are automatically synced to [GitLab](https://gitlab.iimlab.id/business-process/LIBRARY-BPMN_Graph_Transformation) for automated publishing

---

## 🔗 Related Tools

- [BPMN.io](https://bpmn.io/) - BPMN modeling toolkit
- [Camunda](https://camunda.com/) - Workflow and decision automation
- [Neo4j](https://neo4j.com/) - Graph database platform

---

**Developed by IIM Lab (Lab MCI), Informatics Department, Institut Teknologi Sepuluh Nopember**