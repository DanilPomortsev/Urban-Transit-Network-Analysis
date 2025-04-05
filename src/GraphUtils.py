def to_bus_graph(nodes, rels):
    rels_list = {}
    for node in nodes.values:
        rels_list[node[4]] = []
    for rel in rels.values:
        rels_list[rel[0]].append(rel[1])
    return (nodes, rels_list)