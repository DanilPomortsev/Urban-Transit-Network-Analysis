import math
from abc import abstractmethod

import osmnx as ox
import pandas as pd
import quads

from context import GraphAnalisContext
from database.Neo4jConnection import Neo4jConnection
from parser.Parser import BusGraphParser, TrolleyGraphParser, TramGraphParser, MiniBusGraphParser
"""
    Классы с наследственной структурой которые занимаются работой с бд для каждого типа сети 
"""


class GraphDBManager:
    def __init__(self, graph_analis_context: GraphAnalisContext):
        self.connection = Neo4jConnection()
        self.city_name = graph_analis_context.city_name
        self.enrichDBParameters(graph_analis_context)
        self.db_graph_parameters = graph_analis_context.neo4j_DB_graph_parameters

    def enrichDBParameters(self, graph_analis_context: GraphAnalisContext):
        graph_analis_context.neo4j_DB_graph_parameters.city_name = self.city_name
        graph_analis_context.neo4j_DB_graph_parameters.node_geometry_identity = self.node_geometry_identity()
        graph_analis_context.neo4j_DB_graph_parameters.main_rels_name = self.get_main_rels_name()
        graph_analis_context.neo4j_DB_graph_parameters.main_node_name = self.get_main_node_name()
        graph_analis_context.neo4j_DB_graph_parameters.weight = self.get_weight()

    @abstractmethod
    def get_graph(self):
        pass

    @abstractmethod
    def get_weight(self):
        pass

    @abstractmethod
    def get_main_node_name(self):
        pass

    @abstractmethod
    def get_main_rels_name(self):
        pass

    @abstractmethod
    def node_geometry_identity(self):
        pass


class TwoTypeNodeDBManager(GraphDBManager):
    def __init__(self, graph_analis_context: GraphAnalisContext):
        super().__init__(graph_analis_context)
        graph_analis_context.neo4j_DB_graph_parameters.secondary_node_name = self.get_second_node_name()
        graph_analis_context.neo4j_DB_graph_parameters.secondary_rels_name = self.get_second_rels_name()
        self.db_graph_parameters.secondary_node_name = self.get_second_node_name()
        self.db_graph_parameters.secondary_rels_name = self.get_second_rels_name()

    def update_db(self):
        (first_nodes, first_relationships, second_nodes, second_relationships) = self.get_graph()
        if first_nodes is None and first_relationships is None and second_nodes is None and second_relationships is None:
            print("Graph for", self.city_name, "is empty!")
            return
        self.connection.execute_write(self.create_constraints)
        self.connection.execute_write(insert_data, self.create_first_node_query(), first_nodes)
        self.connection.execute_write(insert_data, self.create_first_relationships_query(), first_relationships)
        self.connection.execute_write(insert_data, self.create_second_node_query(), second_nodes)
        self.connection.execute_write(insert_data, self.create_second_relationships_query(), second_relationships)

    @abstractmethod
    def get_first_node_name(self):
        pass

    @abstractmethod
    def get_first_rels_name(self):
        pass

    @abstractmethod
    def get_second_node_name(self):
        pass

    @abstractmethod
    def get_second_rels_name(self):
        pass

    def create_constraints(self, tx):
        constraints = self.get_constraint_list()
        for constraint in constraints:
            tx.run(constraint)

    @abstractmethod
    def get_constraint_list(self):
        pass

    @abstractmethod
    def create_first_node_query(self):
        pass

    @abstractmethod
    def create_second_node_query(self):
        pass

    @abstractmethod
    def create_first_relationships_query(self):
        pass

    @abstractmethod
    def create_second_relationships_query(self):
        pass


class RoadBuildingsDbManager(TwoTypeNodeDBManager):
    def get_road_graph(self):
        g = ox.graph_from_place(self.city_name, simplify=True, retain_all=True, network_type="drive")

        gdf_nodes, gdf_relationships = ox.graph_to_gdfs(g)
        gdf_nodes.reset_index(inplace=True)
        gdf_relationships.reset_index(inplace=True)
        gdf_nodes["geometry_wkt"] = gdf_nodes["geometry"].apply(lambda x: x.wkt)
        gdf_relationships["geometry_wkt"] = gdf_relationships["geometry"].apply(lambda x: x.wkt)

        return gdf_nodes.drop(columns=["geometry"]), gdf_relationships.drop(columns=["geometry"])

    def get_graph(self):
        (road_nodes, road_relationships) = self.get_road_graph()
        tree = quads.QuadTree((0, 0), 200, 200)
        road_geo_to_node = {quads.Point(float(road_node.x), float(road_node.y)): road_node for road_node in
                            road_nodes.itertuples()}
        for road_node in road_nodes.itertuples():
            tree.insert((float(road_node.x), float(road_node.y)))
        buildings = pd.DataFrame(ox.geometries_from_place(self.city_name, tags={'building': True}))
        buildings = buildings.rename(columns={'addr:street': 'street', 'addr:housenumber': 'housenumber'})
        buildings_rels = []
        filtred_buildings = []
        i = 0
        for building in buildings.itertuples():
            print(i)
            i += 1
            if building.geometry.geom_type == "Polygon" or building.geometry.geom_type == "MultiPolygon":
                x = building.geometry.centroid.x
                y = building.geometry.centroid.y
            else:
                x, y = building.geometry.coords[0]
            nearest_point = tree.nearest_neighbors((x, y), 1)
            nearest_node = road_geo_to_node[nearest_point[0]]
            uniq_name = str(building.Index) + str(x) + str(y)
            nearest_node_filtred = {
                "intersect_osmid": nearest_node.osmid,
                "uniq_building_name": uniq_name,
                "uniq_building_road_name": uniq_name + "to" + str(nearest_node.x) + str(nearest_node.y),
                "length": math.sqrt((nearest_node.x - x) ** 2 + (nearest_node.y - y) ** 2)
            }
            buildings_rels.append(nearest_node_filtred)
            filtred_building = {
                "uniq_building_name": uniq_name,
                "building": getattr(building, "building", None),
                "name": getattr(building, "name", None),
                "street": getattr(building, "street", None),
                "housenumber": getattr(building, "housenumber", None),
                "amenity": getattr(building, "amenity", None),
                "phone": getattr(building, "phone", None),
                "shop": getattr(building, "shop", None),
                "year_of_construction": getattr(building, "year_of_construction", None),
                "opening_hours": getattr(building, "opening_hours", None),
                "x": x,
                "y": y
            }
            filtred_buildings.append(filtred_building)
        return (road_nodes, road_relationships, filtred_buildings, buildings_rels)

    def get_first_node_name(self):
        return self.city_name + "Intersection"

    def get_first_rels_name(self):
        return self.city_name + "Road"

    def get_second_node_name(self):
        return self.city_name + "Building"

    def get_second_rels_name(self):
        return self.city_name + "BuildingToNearestIntersection"

    def get_constraint_list(self):
        return [
            r"CREATE CONSTRAINT IF NOT EXISTS FOR (i:{}) REQUIRE i.osmid IS UNIQUE".format(self.db_graph_parameters.main_node_name),
            r"CREATE INDEX IF NOT EXISTS FOR ()-[r:{}]-() ON r.osmid".format(self.db_graph_parameters.main_rels_name),
            r"CREATE CONSTRAINT IF NOT EXISTS FOR (i:{}) REQUIRE i.uniq_building_name IS UNIQUE"
            .format(self.db_graph_parameters.secondary_node_name),
            r"CREATE INDEX IF NOT EXISTS FOR ()-[r:{}]-() ON r.uniq_building_road_name"
            .format(self.db_graph_parameters.secondary_rels_name),
        ]

    def create_first_node_query(self):
        return f'''
        UNWIND $rows AS row
        WITH row WHERE row.osmid IS NOT NULL
        MERGE (i:{self.db_graph_parameters.main_node_name} {{osmid: row.osmid}})
            SET i.location = point({{latitude: row.y, longitude: row.x }}),
                i.highway = row.highway,
                i.tram = row.tram,
                i.bus = row.bus,
                i.geometry_wkt = row.geometry_wkt,
                i.street_count = toInteger(row.street_count)
        RETURN COUNT(*) as total
        '''

    def create_second_node_query(self):
        return f"""
        UNWIND $rows AS row
        WITH row WHERE row.uniq_building_name IS NOT NULL
        MERGE (i:{self.db_graph_parameters.secondary_node_name} {{uniq_building_name: row.uniq_building_name}})
            SET i.building = row.building,
                i.name = row.name,
                i.street = row.street,
                i.housenumber = row.housenumber,
                i.amenity = row.amenity,
                i.phone = row.phone,
                i.shop = row.shop,
                i.year_of_construction = row.year_of_construction,
                i.opening_hours = row.opening_hours,
                i.location = point({{latitude: row.y, longitude: row.x }})
        RETURN COUNT(*) as total
    """

    def create_first_relationships_query(self):
        return f'''
        UNWIND $rows AS path
        MATCH (u:{self.db_graph_parameters.main_node_name} {{osmid: path.u}})
        MATCH (v:{self.db_graph_parameters.main_node_name} {{osmid: path.v}})
        MERGE (u)-[r:{self.db_graph_parameters.main_rels_name} {{osmid: path.osmid}}]->(v)
            SET r.name = path.name,
                r.highway = path.highway,
                r.railway = path.railway,
                r.oneway = path.oneway,
                r.lanes = path.lanes,
                r.max_speed = path.maxspeed,
                r.geometry_wkt = path.geometry_wkt,
                r.length = toFloat(path.length)
        RETURN COUNT(*) AS total
        '''

    def create_second_relationships_query(self):
        return f'''
        UNWIND $rows AS path
        MATCH (u:{self.db_graph_parameters.main_node_name} {{osmid: path.intersect_osmid}})
        MATCH (v:{self.db_graph_parameters.secondary_node_name} {{ uniq_building_name: path.uniq_building_name}})
        MERGE (u)-[r:{self.db_graph_parameters.secondary_rels_name} {{uniq_building_road_name: path.uniq_building_road_name}}]->(v)
            SET r.intersect_osmid = path.intersect_osmid,
                r.uniq_building_name = path.uniq_building_name,
                r.length = toFloat(path.length)
        RETURN COUNT(*) AS total
    '''

    def get_main_node_name(self):
        return self.get_main_node_name().replace('-', '')

    def get_main_rels_name(self):
        return self.get_main_rels_name().replace('-', '')

    def get_weight(self):
        return "length"


class OneTypeNodeDBManager(GraphDBManager):
    def __init__(self, graph_analisis_context: GraphAnalisContext):
        super().__init__(graph_analisis_context)

    def update_db(self, city_name):
        (nodes, relationships) = self.get_graph()
        if nodes is None and relationships is None:
            print("Graph for", city_name, "is empty!")
            return
        self.connection.execute_write(self.create_constraints)
        self.connection.execute_write(insert_data, self.create_node_query(), nodes)
        self.connection.execute_write(insert_data, self.create_relationships_query(), relationships)

    @abstractmethod
    def get_bd_all_node_query_graph(self):
        pass

    @abstractmethod
    def get_bd_all_rels_query_graph(self):
        pass

    @abstractmethod
    def get_node_name(self):
        pass

    @abstractmethod
    def get_rels_name(self):
        pass

    def get_bd_all_node_graph(self):
        node_get_query = self.get_bd_all_node_query_graph()
        return self.connection.read_all(node_get_query)

    def get_bd_all_rels_graph(self):
        rels_get_query = self.get_bd_all_rels_query_graph()
        return self.connection.read_all(rels_get_query)

    def create_constraints(self, tx):
        constraints = self.get_constraint_list()
        for constraint in constraints:
            tx.run(constraint)

    def get_main_node_name(self):
        return self.get_node_name().replace('-', '')

    def get_main_rels_name(self):
        return self.get_rels_name().replace('-', '')

    @abstractmethod
    def get_constraint_list(self):
        pass

    @abstractmethod
    def create_node_query(self):
        pass

    @abstractmethod
    def create_relationships_query(self):
        pass


class TransportNetworkGraphDBManager(OneTypeNodeDBManager):
    def create_node_query(self):
        return f'''
            UNWIND $rows AS row
            WITH row WHERE row.name IS NOT NULL
            MERGE (s:{self.db_graph_parameters.main_node_name} {{name: row.name}})
                SET s.location = point({{latitude: row.yCoordinate, longitude: row.xCoordinate }}),
                    s.roteList = row.roteList,
                    s.isCoordinateApproximate = row.isCoordinateApproximate
            RETURN COUNT(*) AS total
        '''

    def create_relationships_query(self):
        return f'''
            UNWIND $rows AS path
            MATCH (u:{self.db_graph_parameters.main_node_name} {{name: path.startStop}})
            MATCH (v:{self.db_graph_parameters.main_node_name} {{name: path.endStop}})
            MERGE (u)-[r:{self.db_graph_parameters.main_rels_name} {{name: path.name}}]->(v)
                SET r.duration = path.duration,
                    r.route = path.route
            RETURN COUNT(*) AS total
        '''

    def get_bd_all_node_query_graph(self):
        return f'''
        MATCH (s:Stop)
        RETURN 
            ID(s) AS id,
            s.roteList AS roteList, 
            s.location.longitude AS x, 
            s.location.latitude AS y, 
            s.name AS name, 
            s.isCoordinateApproximate AS isCoordinateApproximate
        '''

    def get_bd_all_rels_query_graph(self):
        return f'''
        MATCH (u:Stop)-[r:{self.db_graph_parameters.main_rels_name}]->(v:Stop) 
        RETURN
            u.name AS first_stop_name, 
            v.name AS second_stop_name, 
            r.duration AS duration
        '''

    def get_constraint_list(self):
        return [
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (s:{self.db_graph_parameters.main_node_name}) REQUIRE s.name IS UNIQUE",
            f"CREATE INDEX IF NOT EXISTS FOR ()-[r:{self.db_graph_parameters.main_rels_name}]-() ON r.name"
        ]

    @abstractmethod
    def get_graph(self):
        pass

    @abstractmethod
    def get_node_name(self):
        pass

    @abstractmethod
    def get_rels_name(self):
        pass

    @abstractmethod
    def get_weight(self):
        pass


class RoadGraphDBManager(OneTypeNodeDBManager):

    def get_graph(self):
        g = ox.graph_from_place(self.city_name, simplify=True, retain_all=True, network_type="drive")

        gdf_nodes, gdf_relationships = ox.graph_to_gdfs(g)
        gdf_nodes.reset_index(inplace=True)
        gdf_relationships.reset_index(inplace=True)
        gdf_nodes["geometry_wkt"] = gdf_nodes["geometry"].apply(lambda x: x.wkt)
        gdf_relationships["geometry_wkt"] = gdf_relationships["geometry"].apply(lambda x: x.wkt)

        return gdf_nodes.drop(columns=["geometry"]), gdf_relationships.drop(columns=["geometry"])

    def create_node_query(self):
        return f'''
        UNWIND $rows AS row
        WITH row WHERE row.osmid IS NOT NULL
        MERGE (i:{self.db_graph_parameters.main_node_name} {{osmid: row.osmid}})
            SET i.location = point({{latitude: row.y, longitude: row.x }}),
                i.highway = row.highway,
                i.tram = row.tram,
                i.bus = row.bus,
                i.geometry_wkt = row.geometry_wkt,
                i.street_count = toInteger(row.street_count)
        RETURN COUNT(*) as total
        '''

    def create_relationships_query(self):
        return f'''
        UNWIND $rows AS path
        MATCH (u:{self.db_graph_parameters.main_node_name} {{osmid: path.u}})
        MATCH (v:{self.db_graph_parameters.main_node_name} {{osmid: path.v}})
        MERGE (u)-[r:{self.db_graph_parameters.main_rels_name} {{osmid: path.osmid}}]->(v)
            SET r.name = path.name,
                r.highway = path.highway,
                r.railway = path.railway,
                r.oneway = path.oneway,
                r.lanes = path.lanes,
                r.max_speed = path.maxspeed,
                r.geometry_wkt = path.geometry_wkt,
                r.length = toFloat(path.length)
        RETURN COUNT(*) AS total
        '''

    def get_constraint_list(self):
        return [
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (i:{self.db_graph_parameters.main_node_name}) REQUIRE i.osmid IS UNIQUE",
            f"CREATE INDEX IF NOT EXISTS FOR ()-[r:{self.db_graph_parameters.main_rels_name}]-() ON r.osmid"
        ]

    def get_bd_all_node_query_graph(self):
        return f'''
        MATCH (s:{self.db_graph_parameters.main_node_name})
        RETURN 
            ID(s) AS id,
            s.highway AS highway,
            s.location.longitude AS x, 
            s.location.latitude AS y, 
            s.tram AS tram,
            s.bus AS bus, 
            s.geometry_wkt AS geometry_wkt,
            s.street_count AS street_count
        '''

    def get_bd_all_rels_query_graph(self):
        return f'''
        MATCH (u:{self.db_graph_parameters.main_node_name})-[r:{self.db_graph_parameters.main_rels_name}]->(v:{self.db_graph_parameters.main_node_name}) 
        RETURN
            u.osmid AS first_osmid, 
            v.osmid AS second_osmid, 
            r.name AS name,
            r.highway AS highway,
            r.railway AS railway,
            r.oneway AS oneway,
            r.lanes AS lanes,
            r.max_speed AS maxspeed,
            r.geometry_wkt AS geometry_wkt,
            r.length AS length
        '''

    def get_node_name(self):
        return self.city_name + "Intersection"

    def get_rels_name(self):
        return self.city_name + "RoadSegment"

    def get_weight(self):
        return "length"

    def node_geometry_identity(self):
        return "geometry_wkt"


class BusGraphDBManager(TransportNetworkGraphDBManager):

    def get_graph(self):
        parser = BusGraphParser(self.city_name)
        (nodes, relationships) = parser.parse()
        return list(nodes.values()), relationships

    def get_node_name(self):
        return self.city_name + "BusStop"

    def get_rels_name(self):
        return self.city_name + "BusRouteSegment"

    def get_weight(self):
        return "duration"

    def node_geometry_identity(self):
        return "location"


class TrolleyGraphDBManager(TransportNetworkGraphDBManager):
    def get_graph(self):
        parser = TrolleyGraphParser(self.city_name)
        (nodes, relationships) = parser.parse()
        return list(nodes.values()), relationships

    def get_node_name(self):
        return self.city_name + "TrolleyStop"

    def get_rels_name(self):
        return self.city_name + "TrolleyRouteSegment"

    def get_weight(self):
        return "duration"


class TramGraphDBManager(TransportNetworkGraphDBManager):
    def get_graph(self):
        parser = TramGraphParser(self.city_name)
        (nodes, relationships) = parser.parse()
        return list(nodes.values()), relationships

    def get_node_name(self):
        return self.city_name + "TramStop"

    def get_rels_name(self):
        return self.city_name + "TramRouteSegment"

    def get_weight(self):
        return "duration"


class MiniBusGraphDBManager(TransportNetworkGraphDBManager):
    def get_graph(self):
        parser = MiniBusGraphParser(self.city_name)
        (nodes, relationships) = parser.parse()
        return list(nodes.values()), relationships

    def get_node_name(self):
        return self.city_name + "MiniBusStop"

    def get_rels_name(self):
        return self.city_name + "MiniBusRouteSegment"

    def get_weight(self):
        return "duration"


def insert_data(tx, query, rows, batch_size=10000):
    total = 0
    batch = 0

    df = pd.DataFrame(rows)

    while batch * batch_size < len(df):
        current_batch = df.iloc[batch * batch_size:(batch + 1) * batch_size]
        batch_data = current_batch.to_dict('records')
        results = tx.run(query, parameters={'rows': batch_data}).data()
        print(results)
        total += results[0]['total']
        batch += 1
    return total
