def generate_pools_lanes(elements, process_id=None):
    cypher = []

    for pool in elements.get("pools", []):
        cypher.append(
            f"CREATE (:Pool {{id: '{pool['id']}', name: '{pool.get('name', '')}', type: '{pool.get('type', '')}', "
            f"process_ref: '{pool.get('process_ref', '')}', process_id: '{process_id}'}});"
        )

    for lane in elements.get("lanes", []):
        pool_id = lane.get("pool_id", "")  # fallback jika tidak ada
        cypher.append(
            f"CREATE (:Lane {{id: '{lane['id']}', name: '{lane.get('name', '')}', type: '{lane.get('type', '')}', "
            f"pool_id: '{pool_id}', process_id: '{process_id}'}});"
        )

        # hanya buat relasi jika pool_id ada
        if pool_id:
            cypher.append(
                f"MATCH (l:Lane {{id: '{lane['id']}'}}) WITH l "
                f"MATCH (p:Pool {{id: '{pool_id}'}}) "
                f"CREATE (l)-[:BELONGS_TO]->(p);"
            )

    return cypher
