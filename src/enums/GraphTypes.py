from enum import Enum
import src.database.GraphDbManager as GraphDbManager


class GraphTypes(Enum):
    ROAD_GRAPH = GraphDbManager.RoadGraphDBManager
    ROAD_BUILDINGS_GRAPH = GraphDbManager.RoadBuildingsDbManager
    BUS_GRAPH = GraphDbManager.BusGraphDBManager
    TRAM_GRAPH = GraphDbManager.TramGraphDBManager
    TROLLEY_GRAPH = GraphDbManager.TrolleyGraphDBManager
    MINIBUS_GRAPH = GraphDbManager.MiniBusGraphDBManager