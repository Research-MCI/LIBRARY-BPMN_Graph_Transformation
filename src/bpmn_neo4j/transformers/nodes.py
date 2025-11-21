import json

def generate_nodes(elements, process_id=None):
    cypher = []

    def to_cypher_value(val):
        return 'null' if val is None else json.dumps(val)

    # 🔍 Buat mapping dari pool_id → pool_name dan process_ref → pool_name
    pool_map = {p["id"]: p.get("name", "") for p in elements.get("pools", [])}
    pool_ref_map = {p.get("process_ref"): p.get("name", "") for p in elements.get("pools", [])}
    lane_map = {l["id"]: l.get("name", "") for l in elements.get("lanes", [])}

    # =========================
    # ACTIVITY NODES
    # =========================
    for act in elements.get("activities", []):
        pool_id = act.get("pool_id")
        lane_id = act.get("lane_id")

        # Cari pool_name dari pool_id atau process_ref
        pool_name = pool_map.get(pool_id, "") or pool_ref_map.get(pool_id, "")
        lane_name = lane_map.get(lane_id, "")

        cypher.append(
            f"CREATE (a:Activity {{"
            f"id: '{act['id']}', "
            f"name: {json.dumps(act.get('name', ''))}, "
            f"type: '{act['type']}', "
            f"pool_id: {to_cypher_value(pool_id)}, "
            f"lane_id: {to_cypher_value(lane_id)}, "
            f"pool_name: {json.dumps(pool_name)}, "
            f"lane_name: {json.dumps(lane_name)}, "
            f"process_id: '{process_id}'}});"
        )

    # =========================
    # EVENT NODES
    # =========================
    for evt in elements.get("events", []):
        name = evt.get("name", "")
        event_type = evt.get("event_type") or evt.get("type") or ""
        if not name.strip():
            if "start" in event_type.lower():
                name = "Start"
            elif "end" in event_type.lower():
                name = "End"

        pool_id = evt.get("pool_id")
        lane_id = evt.get("lane_id")

        # Cari pool_name dari pool_id atau process_ref
        pool_name = pool_map.get(pool_id, "") or pool_ref_map.get(pool_id, "")
        lane_name = lane_map.get(lane_id, "")

        cypher.append(
            f"CREATE (e:Event {{"
            f"id: '{evt['id']}', "
            f"name: {json.dumps(name)}, "
            f"type: '{evt['type']}', "
            f"event_type: '{event_type}', "
            f"bpmn_type: '{event_type}', "
            f"pool_id: {to_cypher_value(pool_id)}, "
            f"lane_id: {to_cypher_value(lane_id)}, "
            f"pool_name: {json.dumps(pool_name)}, "
            f"lane_name: {json.dumps(lane_name)}, "
            f"process_id: '{process_id}'}});"
        )

    return cypher
