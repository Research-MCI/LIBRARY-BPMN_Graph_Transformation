import uuid
import json

def normalize_json_structure(data):
    if "result" in data and isinstance(data["result"], dict):
        for key in ["flowElements", "pools", "lanes", "messageFlows"]:
            if key in data["result"]:
                data[key] = data["result"][key]
    return data


def map_flows_to_source_target(elements):
    flow_map = {}

    for el in elements:
        el_id = el.get("id")
        el_name = el.get("name", "")
        el_type = el.get("type", "").lower()

        # Untuk messageFlow (special case)
        if "messageflow" in el_type:
            for src in el.get("incoming", []):
                flow_map.setdefault(el_id, {})["source"] = src
                flow_map[el_id]["source_name"] = ""
            for tgt in el.get("outgoing", []):
                flow_map.setdefault(el_id, {})["target"] = tgt
                flow_map[el_id]["target_name"] = ""
            continue

        # Flow biasa
        for out_flow in el.get("outgoing", []):
            flow_map.setdefault(out_flow, {})["source"] = el_id
            flow_map[out_flow]["source_name"] = el_name

        for in_flow in el.get("incoming", []):
            flow_map.setdefault(in_flow, {})["target"] = el_id
            flow_map[in_flow]["target_name"] = el_name

    return flow_map


def normalize_flow_elements(data, process_id=None):
    data = normalize_json_structure(data)
    elements = (data.get("flowElements", []) or []) + (data.get("messageFlows", []) or [])
    process_id = process_id or data.get("process_id") or str(uuid.uuid4())

    element_by_id = {el.get("id"): el for el in elements}
    flow_map = map_flows_to_source_target(elements)

    result = {
        "activities": [],
        "events": [],
        "gateways": [],
        "flows": [],
        "pools": data.get("pools", []) or [],
        "lanes": data.get("lanes", []) or [],
    }

    pools_raw = result["pools"]
    lanes_raw = result["lanes"]

    # 🔧 Mapping pool name berdasarkan ID dan processRef
    pool_name_by_id = {p.get("id"): p.get("name", "") for p in pools_raw}
    pool_name_by_ref = {}
    for p in pools_raw:
        for ref in {p.get("processRef"), p.get("process_ref"), p.get("processId"), p.get("id")}:
            if ref:
                pool_name_by_ref[ref] = p.get("name", "")

    # 🔧 Mapping lane name berdasarkan ID
    lane_name_map = {l.get("id"): l.get("name", "") for l in lanes_raw}

    def _normalize_id(val):
        if not val:
            return None
        if isinstance(val, str):
            s = val.strip().lower()
            if s in ("", "none", "null"):
                return None
            return val.strip()
        return val

    # ===============================================================
    # 🔧 PROSES NORMALISASI ELEMEN
    # ===============================================================
    for el in elements:
        raw_type = el.get("type", "") or ""
        el_type = raw_type.lower()
        sub_type = (el.get("subType") or "").lower()

        if not sub_type:
            if "startevent" in el_type:
                sub_type = "startEvent"
            elif "endevent" in el_type:
                sub_type = "endEvent"
            elif "intermediate" in el_type:
                sub_type = "intermediateEvent"
            elif "exclusivegateway" in el_type:
                sub_type = "exclusiveGateway"
            elif "parallelgateway" in el_type:
                sub_type = "parallelGateway"
            elif "inclusivegateway" in el_type:
                sub_type = "inclusiveGateway"
            elif "eventbasedgateway" in el_type or el.get("eventGatewayType"):
                sub_type = "eventBasedGateway"

        element_id = el.get("id")
        name = el.get("name", "") or ""
        props = el.get("properties", {}) or {}

        pool_id = (
            props.get("pool_id")
            or el.get("pool_id")
            or el.get("process_id")
            or el.get("processRef")
        )
        lane_id = props.get("lane_id") or el.get("lane_id")

        pool_id = _normalize_id(pool_id)
        lane_id = _normalize_id(lane_id)

        # ===============================================================
        # 🔧 Pencarian pool_name dan lane_name
        # ===============================================================
        pool_name = ""
        if pool_id:
            pool_name = (
                pool_name_by_id.get(pool_id)
                or pool_name_by_ref.get(pool_id)
                or ""
            )

        # Jika belum ketemu, cari lewat process_ref
        if not pool_name:
            proc = el.get("process_id") or data.get("process_id") or process_id
            pool_name = (
                pool_name_by_ref.get(proc, "")
                or pool_name_by_ref.get(pool_id, "")
                or ""
            )

        lane_name = lane_name_map.get(lane_id, "") if lane_id else ""

        # ===============================================================
        # 🔹 FLOW
        # ===============================================================
        if "flow" in el_type:
            flow_id = element_id
            flow_info = flow_map.get(flow_id, {})
            source_id = flow_info.get("source")
            target_id = flow_info.get("target")

            source_el = element_by_id.get(source_id, {}) or {}
            target_el = element_by_id.get(target_id, {}) or {}

            source_props = source_el.get("properties", {}) or {}
            target_props = target_el.get("properties", {}) or {}

            src_pool_id = _normalize_id(
                source_props.get("pool_id") or source_el.get("pool_id") or source_el.get("process_id")
            )
            tgt_pool_id = _normalize_id(
                target_props.get("pool_id") or target_el.get("pool_id") or target_el.get("process_id")
            )

            src_pool_name = (
                pool_name_by_id.get(src_pool_id)
                or pool_name_by_ref.get(src_pool_id)
                or pool_name_by_ref.get(source_el.get("process_id"))
                or ""
            )
            tgt_pool_name = (
                pool_name_by_id.get(tgt_pool_id)
                or pool_name_by_ref.get(tgt_pool_id)
                or pool_name_by_ref.get(target_el.get("process_id"))
                or ""
            )

            src_lane_id = _normalize_id(source_props.get("lane_id") or source_el.get("lane_id"))
            tgt_lane_id = _normalize_id(target_props.get("lane_id") or target_el.get("lane_id"))

            src_lane_name = lane_name_map.get(src_lane_id, "") if src_lane_id else ""
            tgt_lane_name = lane_name_map.get(tgt_lane_id, "") if tgt_lane_id else ""

            # 🔹 Tentukan jenis flow
            flow_type = "messageflow" if "message" in el_type else "sequenceflow"

            gateway_id = None
            if source_el.get("type", "").lower().endswith("gateway"):
                gateway_id = source_id
            elif target_el.get("type", "").lower().endswith("gateway"):
                gateway_id = target_id



            result["flows"].append({
                "id": flow_id,
                "name": name,
                "type": sub_type or el_type,
                "flow_type": flow_type,
                "source": source_id,
                "target": target_id,
                "gateway_id": gateway_id,
                "source_name": flow_info.get("source_name", ""),
                "target_name": flow_info.get("target_name", ""),
                "pool_name": src_pool_name or tgt_pool_name or pool_name,
                "lane_name": src_lane_name or tgt_lane_name or lane_name,
                "source_pool_name": src_pool_name,
                "target_pool_name": tgt_pool_name,
                "source_lane_name": src_lane_name,
                "target_lane_name": tgt_lane_name,
                "process_id": process_id,
            })
            continue

        # ===============================================================
        # 🔹 ACTIVITY
        # ===============================================================
        if "task" in el_type:
            result["activities"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "pool_id": pool_id,
                "lane_id": lane_id,
                "pool_name": pool_name,
                "lane_name": lane_name,
                "process_id": process_id
            })

        # ===============================================================
        # 🔹 GATEWAY
        # ===============================================================
        elif "gateway" in el_type or "eventbasedgateway" in el_type:
            gw_type = sub_type or el.get("gateway_type") or el_type
            result["gateways"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "gateway_type": gw_type.lower(),
                "pool_id": pool_id,
                "lane_id": lane_id,
                "pool_name": pool_name,
                "lane_name": lane_name,
                "process_id": process_id
            })

        # ===============================================================
        # 🔹 EVENT
        # ===============================================================
        elif any(x in el_type for x in ["event", "startevent", "endevent"]):
            result["events"].append({
                "id": element_id,
                "name": name,
                "type": el_type,
                "event_type": sub_type or el_type,
                "pool_id": pool_id,
                "lane_id": lane_id,
                "pool_name": pool_name,
                "lane_name": lane_name,
                "process_id": process_id
            })

    # ===============================================================
    # 🔹 LANE dan POOL disederhanakan
    # ===============================================================
    result["pools"] = [
        {
            "id": p.get("id"),
            "name": p.get("name", ""),
            "type": "Pool",
            "process_ref": p.get("processRef", p.get("process_ref", "")),
        }
        for p in pools_raw
    ]

    result["lanes"] = [
        {
            "id": l.get("id"),
            "name": l.get("name", ""),
            "type": "Lane",
        }
        for l in lanes_raw
    ]

    result["process_id"] = process_id
    return result

