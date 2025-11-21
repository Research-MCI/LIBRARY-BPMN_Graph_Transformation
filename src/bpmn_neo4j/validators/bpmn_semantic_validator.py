def validate_semantics(bpmn_json, strict=False):
    """
    Versi baru validator semantik untuk format BPMN JSON:
    bpmn_json["result"]["flowElements"]
    """

    result = bpmn_json.get("result", {})
    flow_elements = result.get("flowElements", [])
    message_flows = result.get("messageFlows", [])
    pools = result.get("pools", [])
    lanes = result.get("lanes", [])

    # Klasifikasi elemen berdasarkan tipe
    activities = [e for e in flow_elements if "task" in e.get("type", "").lower()]
    events = [e for e in flow_elements if "event" in e.get("type", "").lower()]
    gateways = [e for e in flow_elements if "gateway" in e.get("type", "").lower()]
    flows = [e for e in flow_elements if "flow" in e.get("type", "").lower()]

    errors = []
    warnings = []
    outgoing = {}
    incoming = {}

    # === Helper: resolve flow endpoints (support both 'source'/'target' and 'incoming'/'outgoing') ===
    def _resolve_endpoints(elem):
        """Return (source, target) for a flow-like element.

        The parser output sometimes uses 'source'/'target' keys and sometimes
        uses 'incoming' (list) / 'outgoing' (list) where the first item is
        the endpoint id. Prefer explicit keys, then fall back to lists.
        """
        src = elem.get("source")
        tgt = elem.get("target")
        # fallback to incoming/outgoing lists
        if not src:
            inc = elem.get("incoming")
            if isinstance(inc, (list, tuple)) and len(inc) > 0:
                # some formats use incoming:[sourceId]
                src = inc[0]
        if not tgt:
            out = elem.get("outgoing")
            if isinstance(out, (list, tuple)) and len(out) > 0:
                # some formats use outgoing:[targetId]
                tgt = out[0]
        return src, tgt

    # === Build incoming dan outgoing map ===
    for flow in flows:
        source, target = _resolve_endpoints(flow)
        outgoing.setdefault(source, []).append(target)
        incoming.setdefault(target, []).append(source)

    # === Valid IDs ===
    valid_ids = set(obj.get("id") for obj in activities + events + gateways)

    # === Validasi referensi flow ===
    for flow in flows:
        source, target = _resolve_endpoints(flow)
        fid = flow.get("id")
        if source not in valid_ids:
            errors.append(f"[BPMN 0101] Flow '{fid}' has invalid source: '{source}' not found.")
        if target not in valid_ids:
            errors.append(f"[BPMN 0102] Flow '{fid}' has invalid target: '{target}' not found.")

        # BPMN 0202: Sequence flow tidak boleh lintas pool
        if flow.get("type", "").lower() == "sequenceflow":
            src_pool = get_pool(result, source)
            tgt_pool = get_pool(result, target)
            if src_pool and tgt_pool and src_pool != tgt_pool:
                errors.append(f"[BPMN 0202] Sequence flow '{fid}' crosses pool boundary.")

    # === Validasi per kategori ===
    errors += validate_events(events, incoming, outgoing)
    errors += validate_activities(activities, incoming, outgoing)
    errors += validate_gateways(gateways, incoming, outgoing, events)
    errors += validate_orphan_nodes(activities, events, gateways, incoming, outgoing)
    warnings += validate_pool_lane(activities + events + gateways)

    msg_errors, msg_warnings = validate_message_flows(message_flows, result)
    errors += msg_errors
    warnings += msg_warnings

    boundary_errors, boundary_warnings = validate_boundary_event_matching(events)
    errors += boundary_errors
    warnings += boundary_warnings

    label_warnings = validate_event_labels(events)
    warnings += label_warnings

    cond_errors = validate_conditional_sequence_flows(flows, gateways, events, activities)
    errors += cond_errors

    gateway_label_warnings = validate_gateway_labels(gateways, flows)
    warnings += gateway_label_warnings

    # === Statistik konektivitas ===
    connected_nodes = len(set(incoming.keys()) | set(outgoing.keys()))
    total_nodes = len(activities) + len(events) + len(gateways)
    conn_pct = (connected_nodes / total_nodes * 100) if total_nodes > 0 else 0
    print(f"📊 Graph connectivity: {conn_pct:.2f}% of nodes are connected.\n")

    # === Output hasil ===
    if warnings:
        for w in warnings:
            print("⚠️", w)
    if errors:
        print("❌ BPMN semantic rule violations found:")
        for e in errors:
            print("❌", e)
        print(f"❌ Total {len(errors)} violations.\n")
        if strict:
            raise ValueError(f"{len(errors)} BPMN semantic violations found.")
    else:
        print("✅ All BPMN semantic rules are satisfied.\n")


# ==========================================================
# 🔧 Helper dan validator bagian-bagian
# ==========================================================

def get_pool(result, node_id):
    """Cari pool_id berdasarkan elemen dalam flowElements."""
    for node in result.get("flowElements", []):
        if node.get("id") == node_id:
            props = node.get("properties", {})
            return props.get("pool_id") or node.get("pool_id")
    return None


def validate_events(events, incoming, outgoing):
    errors = []
    start_count = 0
    for event in events:
        eid = event.get("id")
        etype = event.get("subType", "").lower() or event.get("type", "").lower()
        trigger = event.get("trigger", None)

        if "start" in etype:
            start_count += 1
            if eid in incoming:
                errors.append(f"[BPMN 0105] Start event '{eid}' must not have incoming flow.")
        elif "end" in etype:
            if eid in outgoing:
                errors.append(f"[BPMN 0124] End event '{eid}' must not have outgoing flow.")
        elif "intermediate" in etype:
            if "throw" in etype and eid not in outgoing:
                errors.append(f"[BPMN 0114] Throwing intermediate event '{eid}' has no outgoing flow.")
            elif "catch" in etype and eid not in incoming:
                errors.append(f"[BPMN 0113] Catching intermediate event '{eid}' has no incoming flow.")
    if start_count > 1:
        errors.append(f"[Style 01106] Only one start event allowed in subprocess.")
    return errors


def validate_activities(activities, incoming, outgoing):
    errors = []
    seen_names = set()
    for task in activities:
        tid = task.get("id")
        tname = (task.get("name") or "").strip()

        if tid not in incoming:
            errors.append(f"[BPMN 0101] Task '{tname or tid}' has no incoming flow.")
        if tid not in outgoing:
            errors.append(f"[BPMN 0102] Task '{tname or tid}' has no outgoing flow.")
        if not tname:
            errors.append(f"[Style 0103] Task '{tid}' should have a label.")
        if tname and tname in seen_names:
            errors.append(f"[Style 0104] Duplicate task name: '{tname}'.")
        seen_names.add(tname)
    return errors


def validate_gateways(gateways, incoming, outgoing, events):
    errors = []
    for gw in gateways:
        gid = gw.get("id")
        gtype = gw.get("subType", "").lower() or gw.get("gateway_type", "").lower()
        in_count = len(incoming.get(gid, []))
        out_count = len(outgoing.get(gid, []))

        # For exclusive/inclusive gateways: require 2+ outgoing only when gateway
        # functions as a diverging (split) gateway. If it's a converging/merge
        # gateway (multiple incoming, single outgoing) then a single outgoing
        # is valid and should not be reported as an error.
        if gtype in ["exclusivegateway", "inclusivegateway"]:
            # treat as diverging if it has <=1 incoming and therefore is splitting
            is_diverging = in_count <= 1
            if is_diverging and out_count < 2:
                errors.append(f"[BPMN 0134] Gateway '{gid}' of type {gtype} should have at least 2 outgoing flows when used as a split.")
        elif gtype == "parallelgateway":
            if in_count < 2 and out_count < 2:
                errors.append(f"[BPMN 0134] Parallel gateway '{gid}' should have at least 2 incoming or 2 outgoing flows.")
        elif gtype == "eventbasedgateway":
            for target_id in outgoing.get(gid, []):
                is_valid = any(
                    e.get("id") == target_id and "intermediatecatch" in e.get("subType", "").lower()
                    for e in events
                )
                if not is_valid:
                    errors.append(f"[BPMN 0138] Event-based gateway '{gid}' must connect to an intermediateCatchEvent.")
    return errors


def validate_orphan_nodes(activities, events, gateways, incoming, outgoing):
    errors = []
    all_nodes = activities + events + gateways
    for node in all_nodes:
        nid = node.get("id")
        ntype = node.get("type", "unknown")
        if nid not in incoming and nid not in outgoing:
            errors.append(f"[Style] Node '{nid}' ({ntype}) is orphaned — no incoming or outgoing flow.")
    return errors


def validate_pool_lane(nodes):
    warnings = []
    for node in nodes:
        nid = node.get("id", "<unknown>")
        props = node.get("properties", {})
        if not props.get("pool_id"):
            warnings.append(f"[Style] Node '{nid}' is not assigned to any pool.")
        if not props.get("lane_id"):
            warnings.append(f"[Style] Node '{nid}' is not assigned to any lane.")
    return warnings


def validate_message_flows(message_flows, result):
    errors = []
    warnings = []
    nodes = {n["id"]: n for n in result.get("flowElements", [])}
    for mf in message_flows:
        mid = mf.get("id")
        # support both explicit 'source'/'target' and 'incoming'/'outgoing' lists
        source = mf.get("source") or (mf.get("incoming")[0] if isinstance(mf.get("incoming"), list) and mf.get("incoming") else None)
        target = mf.get("target") or (mf.get("outgoing")[0] if isinstance(mf.get("outgoing"), list) and mf.get("outgoing") else None)
        src_node = nodes.get(source)
        tgt_node = nodes.get(target)
        if not src_node:
            errors.append(f"[BPMN 0302] Message flow '{mid}' has invalid source '{source}'.")
            continue
        if not tgt_node:
            errors.append(f"[BPMN 0303] Message flow '{mid}' has invalid target '{target}'.")
            continue
        src_pool = get_pool(result, source)
        tgt_pool = get_pool(result, target)
        if src_pool and src_pool == tgt_pool:
            errors.append(f"[BPMN 0301] Message flow '{mid}' connects nodes in the same pool '{src_pool}'.")
        if not mf.get("name", "").strip():
            warnings.append(f"[Style 0304] Message flow '{mid}' should be labeled.")
    return errors, warnings


def validate_boundary_event_matching(events):
    return [], []  # skip for now — optional refinement later


def validate_event_labels(events):
    warnings = []
    for event in events:
        eid = event.get("id")
        name = (event.get("name") or "").strip()
        etype = event.get("subType", "").lower()
        if "start" in etype and not name:
            warnings.append(f"[Style 01105] Start event '{eid}' should be labeled.")
        if "end" in etype and not name:
            warnings.append(f"[Style 0129] End event '{eid}' should be labeled with end state name.")
    return warnings


def validate_conditional_sequence_flows(flows, gateways, events, activities):
    return []  # Optional future rules


def validate_gateway_labels(gateways, flows):
    warnings = []
    outgoing_map = {}
    for flow in flows:
        # resolve source id (support both 'source'/'incoming')
        src = flow.get("source")
        if not src:
            inc = flow.get("incoming")
            if isinstance(inc, (list, tuple)) and len(inc) > 0:
                src = inc[0]
        outgoing_map.setdefault(src, []).append(flow)

    for gw in gateways:
        gid = gw.get("id")
        gtype = gw.get("subType", "").lower()
        outgoing = outgoing_map.get(gid, [])
        unlabeled = [f for f in outgoing if not f.get("name", "").strip()]
        if len(unlabeled) > 1:
            warnings.append(f"[Style 0135] Gateway '{gid}' ({gtype}) has multiple unlabeled outgoing gates.")
        elif len(unlabeled) == 1:
            warnings.append(f"[Style 0136] Gateway '{gid}' has an unlabeled gate.")
    return warnings
