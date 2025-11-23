import json
import jsonschema
from jsonschema import validate
import uuid
import copy
import importlib.resources as pkg_resources
from bpmn_neo4j import validators


def validate_schema(data, schema_path=None, auto_fix=False):

    # --- load schema from package ---
    if schema_path is None:
        with pkg_resources.files(validators).joinpath("bpmn_schema.json").open("r", encoding="utf-8") as f:
            schema = json.load(f)
    else:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    """
    Validasi struktur BPMN JSON dengan format baru (result.flowElements).
    """

    # Pastikan properti 'result' ada
    if "result" not in data:
        print("❌ The 'result' property is missing. This is required in BPMN structure.")
        data["result"] = {}

    # Pastikan struktur utama di dalam 'result' ada
    for key in ["flowElements", "messageFlows", "pools", "lanes"]:
        if key not in data["result"]:
            print(f"⚠️ Warning: The result key '{key}' is missing.")
            data["result"][key] = []

    # 🔍 Ambil flowElements
    flow_elements = data["result"].get("flowElements", [])

    # Deteksi dan perbaiki ID duplikat atau hilang
    if auto_fix:
        fix_missing_ids(data)
        fix_duplicate_ids(data)
    else:
        duplicates = check_duplicate_ids(data)
        if duplicates:
            print(f"❌ Duplicate IDs found: {duplicates}")

    # Deteksi siklus hanya pada flow bertipe "sequenceflow"
    sequence_flows = [f for f in flow_elements if f.get("type", "").lower() == "sequenceflow"]
    if detect_cycle(sequence_flows):
        print("⚠️ Warning: Circular reference detected in sequence flows.")
    else:
        print("✅ No circular dependencies in sequence flows.")

    # Validasi JSON terhadap schema resmi
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
        print("✅ JSON structure is valid against the new BPMN schema.")
        return data
    except jsonschema.exceptions.ValidationError as err:
        print(f"❌ Invalid structure: {err.message}")
        if auto_fix:
            print("🛠️ Attempting to fix the JSON structure automatically...")
            fixed_data = auto_fix_schema(data, schema)
            try:
                validate(instance=fixed_data, schema=schema)
                print("✅ JSON structure has been fixed successfully.")
                return fixed_data
            except jsonschema.exceptions.ValidationError as err2:
                print(f"❌ Structure fixing failed: {err2.message}")
                return fixed_data
        else:
            return data


# 🔁 Cek ID duplikat di semua flowElements
def check_duplicate_ids(data):
    id_set = set()
    duplicates = []

    for el in data["result"].get("flowElements", []):
        iid = el.get("id")
        if iid:
            if iid in id_set:
                duplicates.append(iid)
            id_set.add(iid)
    return duplicates


# ✅ Perbaiki ID duplikat dengan suffix
def fix_duplicate_ids(data):
    print("🛠️ Checking and fixing duplicate IDs...")
    id_count = {}
    for el in data["result"].get("flowElements", []):
        iid = el.get("id")
        if not iid:
            continue
        if iid in id_count:
            id_count[iid] += 1
            new_id = f"{iid}_{id_count[iid]}"
            print(f"⚠️ Duplicate ID '{iid}' found. Renaming to '{new_id}'.")
            el["id"] = new_id
        else:
            id_count[iid] = 0


# ✅ Beri ID default jika hilang
def fix_missing_ids(data):
    print("🛠️ Checking for missing IDs...")
    for el in data["result"].get("flowElements", []):
        if "id" not in el or not el["id"]:
            new_id = f"element_{uuid.uuid4().hex[:6]}"
            print(f"⚠️ Missing ID detected. Assigning ID: {new_id}")
            el["id"] = new_id


# 🧠 Auto-fix berdasarkan JSON schema (rekursif)
def auto_fix_schema(data, schema):
    def fix_object(obj, schema_obj, path="root"):
        if not isinstance(obj, dict):
            return

        required_props = schema_obj.get("required", [])
        properties = schema_obj.get("properties", {})

        # Tambahkan properti wajib yang hilang
        for key in required_props:
            if key not in obj:
                prop_schema = properties.get(key, {})
                default_value = generate_default_value(key, prop_schema, path)
                obj[key] = default_value
                print(f"🛠️ Auto-added missing '{key}' at {path}: {default_value}")

        # Rekursif untuk nested objek
        for key, val in obj.items():
            if key in properties:
                prop_schema = properties[key]
                if isinstance(val, dict) and prop_schema.get("type") == "object":
                    fix_object(val, prop_schema, f"{path}.{key}")
                elif isinstance(val, list) and prop_schema.get("type") == "array":
                    item_schema = prop_schema.get("items", {})
                    for idx, item in enumerate(val):
                        if isinstance(item, dict):
                            fix_object(item, item_schema, f"{path}.{key}[{idx}]")

    def generate_default_value(key, prop_schema, path=""):
        if prop_schema.get("enum"):
            return prop_schema["enum"][0]
        if prop_schema.get("type") == "string":
            if key == "id":
                return f"{path.replace('.', '_')}_{uuid.uuid4().hex[:6]}"
            return f"default_{key}"
        if prop_schema.get("type") == "array":
            return []
        if prop_schema.get("type") == "object":
            return {}
        return None

    fixed_data = copy.deepcopy(data)
    fix_object(fixed_data, schema, path="root")
    return fixed_data


# 🔁 Deteksi siklus hanya untuk sequenceFlow
def detect_cycle(flows):
    from collections import defaultdict, deque

    graph = defaultdict(list)
    indegree = defaultdict(int)
    nodes = set()

    for f in flows:
        src = f.get("source")
        tgt = f.get("target")
        if src and tgt:
            graph[src].append(tgt)
            indegree[tgt] += 1
            nodes.update([src, tgt])

    queue = deque([n for n in nodes if indegree[n] == 0])
    visited = 0

    while queue:
        current = queue.popleft()
        visited += 1
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited != len(nodes)
