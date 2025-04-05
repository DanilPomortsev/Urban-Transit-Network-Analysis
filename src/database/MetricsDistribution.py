from abc import abstractmethod

from src.database.GraphDbManager import GraphDBManager
from src.database.Neo4jConnection import Neo4jConnection


class MetricsDistributionNode:
    def __init__(self, db_manager: GraphDBManager):
        self.node_name = db_manager.node_name
        self.rels_name = db_manager.rels_name
        self.node_identity = db_manager.node_identity
        self.metrics_calculate = self.metrics_calculate()
        self.connection = Neo4jConnection()

    @abstractmethod
    def metrics_calculate(self):
        pass


    def calculate_distribution(self, needLog = False):
        query = f'''
            MATCH (first_node:{self.node_name})
            WITH first_node, {self.metrics_calculate} AS Metric
            RETURN first_node.{self.node_identity} AS NodeIdentity, Metric
            ORDER BY Metric DESC
        '''
        return self.connection.execute_query(query, needLog).records

class DegreeDistribution(MetricsDistributionNode):
    def metrics_calculate(self):
        return 'count(rels)'

    def calculate_distribution(self, needLog = False):
        query = f'''
            MATCH (first_node:{self.node_name})-[rels:{self.rels_name}]-(second_node:{self.node_name})
            WITH first_node, {self.metrics_calculate} AS Metric
            RETURN first_node.{self.node_identity} AS NodeIdentity, Metric
            ORDER BY Metric DESC
        '''
        return self.connection.execute_query(query, needLog).records

class PageRankDistribution(MetricsDistributionNode):
    def metrics_calculate(self):
        return 'first_node.pageRank'

class BetweennessDistribution(MetricsDistributionNode):
    def metrics_calculate(self):
        return 'first_node.betweenness'
