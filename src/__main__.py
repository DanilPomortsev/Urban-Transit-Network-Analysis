from community_detection import Leiden, Louvain
from MetricsCalculate import Betweenness, PageRank
from deep_translator import GoogleTranslator
import osmnx as ox
from graph_db_manager import RoadGraphDBManager,\
                             BusGraphDBManager, \
                             TrolleyGraphDBManager,\
                             TramGraphDBManager, \
                             MiniBusGraphDBManager, \
                             RoadBuildingsDbManager

if __name__ == "__main__":
    ru_city_name = "Петергоф"
    all_types = [
        {
            "name": "Road",
            "dbManagerConstructor": RoadBuildingsDbManager,
        }
    ]

    leiden = Leiden()
    louvain = Louvain()
    betweenessens = Betweenness()
    page_rank = PageRank()
    translator = GoogleTranslator(source='ru', target='en')

    for type_graph in all_types:
        name = type_graph["name"]
        db_manager_constructor = type_graph["dbManagerConstructor"]

        db_manager = db_manager_constructor()
        db_manager.update_db(ru_city_name)

        city_name = translator.translate(ru_city_name).replace(" ", "")
        leiden.detect_communities(
            f"{name}LeidenAlgorithmGraph",
            db_manager.weight,
            db_manager.get_main_node_name(),
            db_manager.get_main_rels_name()
        )
        print(f"LeidenAlgorithm Community detection for graph {name} completed.")
        louvain.detect_communities(
            city_name+f"{name}LouvainAlgorithmGraphTest",
            db_manager.weight,
            db_manager.get_main_node_name(),
            db_manager.get_main_rels_name()
        )
        print(f"LouvainAlgorithm Community detection for graph {name} completed.")
        betweenessens.metric_calculate(
            city_name+f"{name}GraphBetweenessensTest",
            db_manager.weight,
            db_manager.get_main_node_name(),
            db_manager.get_main_rels_name()
        )
        print(f"betweenessens metric calculated for graph {name}.")
        page_rank.metric_calculate(
            city_name+f"{name}GraphPageRankTest",
            db_manager.weight,
            db_manager.get_main_node_name(),
            db_manager.get_main_rels_name()
        )
        print(f"betweenessens metric calculated for graph {name}.")
