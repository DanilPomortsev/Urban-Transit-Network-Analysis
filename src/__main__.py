from community_detection import Leiden, Louvain
from MetricsCalculate import Betweenness, PageRank
from graph_db_manager import RoadGraphDBManager, BusGraphDBManager

if __name__ == "__main__":
    city_name = "Керчь"
    all_types = [
        {
            "name": "Road",
            "nodeName": "Intersection",
            "relationshipName": "RoadSegment",
            "dbManagerConstructor": RoadGraphDBManager,
            'weight': "length"
        },
        {
            "name": "Bus",
            "nodeName": "Stop",
            "relationshipName": "RouteSegment",
            "dbManagerConstructor": BusGraphDBManager,
            'weight': "duration"
        }
    ]

    leiden = Leiden()
    louvain = Louvain()
    betweenessens = Betweenness()
    page_rank = PageRank()

    for type_graph in all_types:
        name = type_graph["name"]
        node_name = type_graph["nodeName"]
        weight = type_graph["weight"]
        relationship_name = type_graph["relationshipName"]
        db_manager_constructor = type_graph["dbManagerConstructor"]

        db_manager = db_manager_constructor(node_name, relationship_name)
        db_manager.update_db(city_name)

        # TODO: road graph not have duration parameter
        leiden.detect_communities(f"{name}Check8LeidenAlgorithmGraph", weight, node_name, relationship_name)
        louvain.detect_communities(f"{name}Check8LouvainAlgorithmGraph", weight, node_name, relationship_name)
        betweenessens.metric_calculate(f"{name}Check8GraphBetweenessens", weight, node_name, relationship_name)
        page_rank.metric_calculate(f"{name}Check8GraphPageRank", weight, node_name, relationship_name)
        print(f"Community detection for graph {name} completed.")
