from abc import abstractmethod

import osmnx as ox
import pandas as pd

from neo4j_connection import Neo4jConnection
from parser import BusGraphParser


class GraphDBManager:
    def __init__(self):
        self.connection = Neo4jConnection()
        self.constraints = []
        self.node_name = self.get_node_name()
        self.rels_name = self.get_rels_name()
        self.weight = self.get_weight()

    def update_db(self, city_name):
        (nodes, relationships) = self.get_graph(city_name)
        if nodes is None and relationships is None:
            print("Graph for", city_name, "is empty!")
            return
        self.connection.execute_write(self.create_constraints)
        self.connection.execute_write(insert_data, self.create_node_query(), nodes)
        self.connection.execute_write(insert_data, self.create_relationships_query(), relationships)

    @abstractmethod
    def get_graph(self, city_name):
        pass

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

    @abstractmethod
    def get_weight(self):
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

    @abstractmethod
    def get_constraint_list(self):
        pass

    @abstractmethod
    def create_node_query(self):
        pass

    @abstractmethod
    def create_relationships_query(self):
        pass

class RoadGraphDBManager(GraphDBManager):

    def get_graph(self, city_name):
        g = ox.graph_from_place(city_name, simplify=True, retain_all=True, network_type="drive")

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
        MERGE (i:{self.get_node_name()} {{osmid: row.osmid}})
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
        MATCH (u:{self.node_name} {{osmid: path.u}})
        MATCH (v:{self.node_name} {{osmid: path.v}})
        MERGE (u)-[r:{self.rels_name()} {{osmid: path.osmid}}]->(v)
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
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (i:{self.node_name}) REQUIRE i.osmid IS UNIQUE",
            f"CREATE INDEX IF NOT EXISTS FOR ()-[r:{self.rels_name}]-() ON r.osmid"
        ]

    def get_bd_all_node_query_graph(self):
        return f'''
        MATCH (s:Stop)
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
        MATCH (u:Stop)-[r:RoadSegment]->(v:Stop) 
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
        return "Intersection"

    def get_rels_name(self):
        return "RoadSegment"

    def get_weight(self):
        return "length"



class BusGraphDBManager(GraphDBManager):

    def get_graph(self, city_name):
        parser = BusGraphParser(city_name)
        (nodes, relationships) = parser.parse()
        return list(nodes.values()), relationships

    def create_node_query(self):
        return f'''
            UNWIND $rows AS row
            WITH row WHERE row.name IS NOT NULL
            MERGE (s:{self.node_name} {{name: row.name}})
                SET s.location = point({{latitude: row.yCoordinate, longitude: row.xCoordinate }}),
                    s.roteList = row.roteList,
                    s.isCoordinateApproximate = row.isCoordinateApproximate
            RETURN COUNT(*) AS total
        '''

    def create_relationships_query(self):
        return f'''
            UNWIND $rows AS path
            MATCH (u:{self.node_name} {{name: path.startStop}})
            MATCH (v:{self.node_name} {{name: path.endStop}})
            MERGE (u)-[r:{self.rels_name} {{name: path.name}}]->(v)
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
        MATCH (u:Stop)-[r:RouteSegment]->(v:Stop) 
        RETURN
            u.name AS first_stop_name, 
            v.name AS second_stop_name, 
            r.duration AS duration
        '''

    def get_constraint_list(self):
        return [
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (s:{self.node_name}) REQUIRE s.name IS UNIQUE",
            f"CREATE INDEX IF NOT EXISTS FOR ()-[r:{self.rels_name}]-() ON r.name"
        ]

    def get_node_name(self):
        return "BusStop"

    def get_rels_name(self):
        return "BusRouteSegment"

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
