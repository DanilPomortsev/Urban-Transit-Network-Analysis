from src.database.Neo4jConnection import Neo4jConnection

"""
    Класс содержащий query для вычисления метрик сети 
"""


class MetricsCalculate:
    def __init__(self, metric_name, write_property):
        self.metric_name = metric_name
        self.write_property = write_property
        self.connection = Neo4jConnection()

    def metric_calculate(self, graph_name, relationship_weight_property, node_name, relationship_name):
        self.__make_graph(graph_name, node_name, relationship_name, relationship_weight_property)
        self.__metric_calculate(graph_name, relationship_weight_property)

    def __make_graph(self, graph_name, node_name, relationship_name, relationship_weight_property):
        query = f'''
            CALL gds.graph.project(
            '{graph_name}',
            '{node_name}',
            {{
                {relationship_name}: {{
                    orientation: 'UNDIRECTED',
                    properties: '{relationship_weight_property}'
                }}
            }}
        )
        '''
        self.connection.run(query)

    def __metric_calculate(self, graph_name, weight_property):
        query = f'''
            CALL gds.{self.metric_name}.write(
                '{graph_name}',
                {{
                relationshipWeightProperty: '{weight_property}',
                writeProperty: '{self.write_property}'
                }}
            )
        '''
        return self.connection.run(query)


class Betweenness(MetricsCalculate):
    def __init__(self):
        super().__init__("betweenness", "betweenness")


class PageRank(MetricsCalculate):
    def __init__(self):
        super().__init__("pageRank", "pageRank")
