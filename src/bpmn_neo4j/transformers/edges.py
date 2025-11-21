import json
import uuid

def build_gateway_map(elements):
    mapping = {}
    for gw in elements.get("gateways", []):
        gw_id = gw.get("id")
        gw_type = (gw.get("gateway_type") or "").lower().strip()
        gw_name = (gw.get("name") or "").lower()

        if not gw_type:
            if "event" in gw_name:
                gw_type = "eventbasedgateway"
            elif "complex" in gw_name:
                gw_type = "complexgateway"
            elif "exclusive" in gw_name:
                gw_type = "exclusivegateway"
            elif "parallel" in gw_name:
                gw_type = "parallelgateway"
            elif "inclusive" in gw_name:
                gw_type = "inclusivegateway"
            else:
                gw_type = "gateway"
        mapping[gw_id] = gw_type
    return mapping


def classify_gateway_direction(gateway_id, incoming, outgoing, gateway_type=None):
    if gateway_type and gateway_type.lower() == "eventbasedgateway":
        return "SPLIT"

    in_count = len(incoming.get(gateway_id, []))
    out_count = len(outgoing.get(gateway_id, []))

    if out_count > 1:
        return "SPLIT"
    elif in_count > 1:
        return "JOIN"
    else:
        return "SINGLE"


def gateway_label(base_type, direction):
    mapping = {
        "exclusivegateway": "XOR",
        "parallelgateway": "AND",
        "inclusivegateway": "OR",
        "complexgateway": "COMPLEX",
        "eventbasedgateway": "EVENT_BASED",
    }

    prefix = mapping.get(base_type.lower(), "GATEWAY")

    if base_type.lower() == "eventbasedgateway":
        direction = "SPLIT"

    if direction in ["SPLIT", "JOIN"]:
        return f"{prefix}_{direction}"
    return prefix

import json
import uuid

# ... pastikan fungsi build_gateway_map, classify_gateway_direction, gateway_label ada di file ...

def generate_edges(elements, process_id=None):
    cypher = []
    gateway_map = build_gateway_map(elements)

    def to_cypher_value(val):
        return 'null' if val is None else json.dumps(val)

    # ambil semua flows awal (message flows juga)
    original_flows = elements.get("flows", []) + elements.get("flows_by_type", {}).get("message_flows", [])

    # --- DETEKSI gateway -> gateway SAAT MASIH BERBENTUK ASLI (hanya sekali) ---
    gateway_chains = set()
    for f in original_flows:
        s, t = f.get("source"), f.get("target")
        if s in gateway_map and t in gateway_map:
            gateway_chains.add(s)
            gateway_chains.add(t)

    # --- buat invisible tasks bila ada gateway->gateway ---
    invisible_tasks = []
    new_flows = []

    for f in list(original_flows):
        src, tgt = f.get("source"), f.get("target")
        if src in gateway_map and tgt in gateway_map:
            # buat invisible task node unik
            invisible_id = f"invisible_{uuid.uuid4().hex[:8]}"
            src_flow_info = next((x for x in original_flows if x.get("source") == src), None)
            prev_node = {
                "pool_id": src_flow_info.get("source_pool") if src_flow_info else None,
                "lane_id": src_flow_info.get("source_lane") if src_flow_info else None,
                "pool_name": src_flow_info.get("source_pool_name") if src_flow_info else None,
                "lane_name": src_flow_info.get("source_lane_name") if src_flow_info else None,
            }

            invisible_tasks.append({
                "id": invisible_id,
                "name": "Invisible Task",
                "type": "InvisibleTask",
                "prev_node": prev_node
            })

            f1 = dict(f)
            f1["id"] = f"{f['id']}_inv_in"
            f1["target"] = invisible_id

            f2 = dict(f)
            f2["id"] = f"{f['id']}_inv_out"
            f2["source"] = invisible_id

            new_flows.extend([f1, f2])
        else:
            new_flows.append(f)

    # gunakan new_flows sebagai all_flows selanjutnya (sudah termasuk invisible flows)
    all_flows = new_flows

    # sekarang bangun incoming/outgoing berdasarkan all_flows yang sudah disesuaikan
    incoming, outgoing = {}, {}
    for flow in all_flows:
        src = flow.get("source")
        tgt = flow.get("target")
        outgoing.setdefault(src, []).append((flow, tgt))
        incoming.setdefault(tgt, []).append((flow, src))

    # set real nodes (termasuk invisible yg akan kita tambahkan)
    real_nodes = {el.get("id") for el in elements.get("activities", []) + elements.get("events", [])}
    seen_edges = set()

    gateway_directions = {
        gid: classify_gateway_direction(gid, incoming, outgoing, gateway_map.get(gid))
        for gid in gateway_map.keys()
    }

    # masukkan invisible tasks sebagai activities agar diakui real node
    for inv in invisible_tasks:
        prev_node = inv.get("prev_node", {})  # ambil gateway/source sebelumnya
        pool_id = prev_node.get("pool_id")
        lane_id = prev_node.get("lane_id")
        pool_name = prev_node.get("pool_name")
        lane_name = prev_node.get("lane_name")

        pool_lane_props = ""
        if pool_id is not None:
            pool_lane_props += f"pool_id: {to_cypher_value(pool_id)}, "
        if lane_id is not None:
            pool_lane_props += f"lane_id: {to_cypher_value(lane_id)}, "
        if pool_name is not None:
            pool_lane_props += f"pool_name: {json.dumps(pool_name)}, "
        if lane_name is not None:
            pool_lane_props += f"lane_name: {json.dumps(lane_name)}, "

        cypher.append(
            f"CREATE (a:Activity {{"
            f"id: '{inv['id']}', "
            f"name: {json.dumps(inv.get('name', 'Invisible Task'))}, "
            f"type: '{inv['type']}', "
            f"{pool_lane_props}"
            f"process_id: '{process_id}'}});"
        )
        real_nodes.add(inv["id"])

    # --- fungsi recursive (TIDAK memblokir hanya berdasarkan gateway_chains) ---
    def find_real_targets(node_id, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            return []
        visited.add(node_id)

        next_targets = []
        for _, tgt in outgoing.get(node_id, []):
            if tgt in real_nodes:
                next_targets.append(tgt)
            elif tgt in outgoing:
                next_targets.extend(find_real_targets(tgt, visited))
        return next_targets

    def find_real_sources(node_id, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited:
            return []
        visited.add(node_id)

        prev_sources = []
        for _, src in incoming.get(node_id, []):
            if src in real_nodes:
                prev_sources.append(src)
            elif src in incoming:
                prev_sources.extend(find_real_sources(src, visited))
        return prev_sources

    # --- BAGIAN PEMBENTUK EDGE --- 
    for flow in all_flows:
        src, tgt = flow.get("source"), flow.get("target")
        rel_name, gtype, direction = "SEQUENCE_FLOW", "", ""
        gateway_id = ""

        flow_type = (flow.get("flow_type") or flow.get("type") or "").lower()
        if "messageflow" in flow_type:
            rel_name = "MESSAGE_FLOW"

        if src in gateway_map:
            gtype = gateway_map[src]
            direction = gateway_directions.get(src, "SINGLE")
            rel_name = gateway_label(gtype, direction)
            gateway_id = src

        elif tgt in gateway_map:
            gtype = gateway_map[tgt]
            direction = gateway_directions.get(tgt, "SINGLE")
            rel_name = gateway_label(gtype, direction)
            gateway_id = tgt

        else:
            src_name = (flow.get("source_name") or "").lower()
            if "gateway" in src_name:
                gtype, direction = "gateway", "SINGLE"
                rel_name = gateway_label(gtype, direction)
                gateway_id = src
            else:
                gateway_id = ""

        rel_name = rel_name.upper().replace(" ", "_").replace("-", "_")
        if not rel_name.isidentifier():
            rel_name = "FLOW"

        props = (
            f"id: '{flow.get('id')}', name: '{flow.get('name','')}', "
            f"type: '{rel_name}', flow_type: '{flow.get('type','SEQUENCE')}', "
            f"gateway_type: '{gtype}', gateway_direction: '{direction}', "
            f"gateway_id: '{gateway_id}', "
            f"source_name: '{flow.get('source_name','')}', target_name: '{flow.get('target_name','')}', "
            f"source_pool: {json.dumps(flow.get('source_pool'))}, source_lane: {json.dumps(flow.get('source_lane'))}, "
            f"target_pool: {json.dumps(flow.get('target_pool'))}, target_lane: {json.dumps(flow.get('target_lane'))}, "
            f"source_pool_name: {json.dumps(flow.get('source_pool_name'))}, "
            f"source_lane_name: {json.dumps(flow.get('source_lane_name'))}, "
            f"target_pool_name: {json.dumps(flow.get('target_pool_name'))}, "
            f"target_lane_name: {json.dumps(flow.get('target_lane_name'))}, "
            f"process_id: '{process_id}'"
        )

        def add_edge(a_id, b_id):
            key = (a_id, b_id)
            if key not in seen_edges:
                seen_edges.add(key)
                cypher.append(
                    f"MATCH (a {{id: '{a_id}'}}) "
                    f"WITH a MATCH (b {{id: '{b_id}'}}) "
                    f"CREATE (a)-[:{rel_name} {{{props}}}]->(b);"
                )

        # event-based gateway special handling (tetap)
        if gtype == "eventbasedgateway":
            targets = [tgt] if tgt in real_nodes else find_real_targets(tgt)
            for real_tgt in targets:
                add_edge(src, real_tgt)
            continue

        # ---- KASUS: src real, tgt non-real (bisa gateway chain) ----
        if src in real_nodes and tgt not in real_nodes:
            # jika target adalah gateway yang termasuk gateway_chains:
            if tgt in gateway_chains:
                # izinkan bypass HANYA jika 'src' memang hanya punya satu outgoing (yaitu ke gateway ini)
                outs = outgoing.get(src, [])
                if len(outs) == 1:
                    # izinkan traversal normal
                    targets = find_real_targets(tgt)
                    for real_tgt in targets:
                        add_edge(src, real_tgt)
                else:
                    # jangan buat direct edges — biarkan Invisible Task meng-handle
                    pass
                continue

            # normal case
            targets = find_real_targets(tgt)
            for real_tgt in targets:
                add_edge(src, real_tgt)
            continue

        # ---- KASUS: src non-real, tgt real (bisa gateway chain di sebelah kiri) ----
        if src not in real_nodes and tgt in real_nodes:
            if src in gateway_chains:
                # izinkan reverse-bypass HANYA jika 'tgt' hanya punya satu incoming (yaitu dari gateway ini)
                ins = incoming.get(tgt, [])
                if len(ins) == 1:
                    sources = find_real_sources(src)
                    for real_src in sources:
                        add_edge(real_src, tgt)
                else:
                    # skip — biarkan Invisible Task meng-handle
                    pass
                continue

            # normal case
            sources = find_real_sources(src)
            for real_src in sources:
                add_edge(real_src, tgt)
            continue

        # ---- kedua tidak real ----
        if src not in real_nodes and tgt not in real_nodes:
            sources = find_real_sources(src)
            targets = find_real_targets(tgt)
            for s in sources:
                for t in targets:
                    add_edge(s, t)
            continue

        # ---- kedua real ----
        if src in real_nodes and tgt in real_nodes:
            add_edge(src, tgt)

    return cypher

