from community_detection import Leiden, Louvain
from MetricsCalculate import Betweenness, PageRank
from graph_db_manager import RoadGraphDBManager, BusGraphDBManager

if __name__ == "__main__":
    city_name = "Керчь"
    all_types = [
        {
            "name": "Road",
            "dbManagerConstructor": RoadGraphDBManager,
        },
        {
            "name": "Bus",
            "dbManagerConstructor": BusGraphDBManager,
        }
    ]

    leiden = Leiden()
    louvain = Louvain()
    betweenessens = Betweenness()
    page_rank = PageRank()

    for type_graph in all_types:
        name = type_graph["name"]
        db_manager_constructor = type_graph["dbManagerConstructor"]

        db_manager = db_manager_constructor()
        db_manager.update_db(city_name)

        # TODO: road graph not have duration parameter
        leiden.detect_communities(
            f"{name}Check8LeidenAlgorithmGraph",
            db_manager.weight,
            db_manager.node_name,
            db_manager.rels_name
        )
        louvain.detect_communities(
            f"{name}Check8LouvainAlgorithmGraph",
            db_manager.weight,
            db_manager.node_name,
            db_manager.rels_name
        )
        betweenessens.metric_calculate(
            f"{name}Check8GraphBetweenessens",
            db_manager.weight,
            db_manager.node_name,
            db_manager.rels_name
        )
        page_rank.metric_calculate(
            f"{name}Check8GraphPageRank",
            db_manager.weight,
            db_manager.node_name,
            db_manager.rels_name
        )
        print(f"Community detection for graph {name} completed.")
