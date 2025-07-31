# 📚 Neo4j Executor Utility

## 🔍 Overview

This module provides a utility class `Neo4jExecutor` that abstracts the connection, query execution, health checks, and batch processing for Neo4j using the official `neo4j` Python driver. It is designed for safe and efficient Cypher query execution, including bulk imports and automatic retries.

## 📂 Location

```
app/
└── core/
    └── repositories/
        └── neo4j_repositories.py
```

## 🚀 Features

- Connection pooling for high performance
- Built-in health check method
- Safe database reset (`MATCH (n) DETACH DELETE n`)
- Automatic index creation for performance optimization
- Batch execution of Cypher queries with retry support
- Execution time reporting and logging

## 🧩 Class: Neo4jExecutor

### `__init__(self, uri, user, password, max_pool_size=50)`

Initializes the Neo4j driver with connection pooling.

- `uri`: Neo4j connection URI (e.g., `bolt://localhost:7687`)
- `user`: Username
- `password`: Password
- `max_pool_size`: Max connection pool size (default: 50)

---

### `close(self)`

Closes the Neo4j connection driver.

---

### `run_health_check(self)`

Returns `True` if the database is responsive, otherwise `False`.

```python
if executor.run_health_check():
    print("Neo4j is healthy!")
```

---

### `setup_indexes(self)`

Creates indexes for `Activity`, `Event`, `Pool`, and `Lane` nodes on their `id` property using:

```cypher
CREATE INDEX IF NOT EXISTS FOR (n:Label) ON (n.id)
```

---

### `run_cypher_lines(self, cypher_lines, reset=False, batch_size=20, retry=3)`

Executes a list of Cypher queries in batches with retry support.

**Parameters:**
- `cypher_lines`: List of raw Cypher strings (one line each)
- `reset`: If `True`, clears the database before execution
- `batch_size`: Number of queries per batch (default: 20)
- `retry`: Number of retry attempts per batch if an error occurs (default: 3)

**Behavior:**
- Filters out comments and blank lines
- Logs each query being executed (truncated for readability)
- Prints total number of executed queries and execution time

**Example usage:**

```python
executor = Neo4jExecutor("bolt://localhost:7687", "neo4j", "password")
executor.setup_indexes()
executor.run_cypher_lines(cypher_lines, reset=True)
executor.close()
```

---

## ⚠️ Notes

- Queries starting with `//` will be ignored
- Each batch will be retried up to 3 times if an exception is thrown
- Logging is printed to console for visibility

---

## 📦 Dependencies

Requires the official Neo4j Python driver:

```bash
pip install neo4j
```

Link: [https://pypi.org/project/neo4j/](https://pypi.org/project/neo4j/)

---

## 📈 Output Example

```
✅ Executing batch 1 (20 queries):
   ➤ CREATE (:Activity {id: "A1", name: "Start"})
   ➤ CREATE (:Event {id: "E1", type: "Start"})
✅ Executing batch 2 (15 queries):
   ...
✅ Total queries executed: 35
⏱️ Total execution time: 1.23s → Avg: 0.0351s/query
```

