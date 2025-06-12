from urban_transit_network_analysis.database.Neo4jConnection import Neo4jConnection

from context import GraphAnalisContext


class AnalysPreparer:
    def __init__(self, graph_analisis_context: GraphAnalisContext):
        self.connection = Neo4jConnection()
        self.graph_db_parameters = graph_analisis_context.neo4j_DB_graph_parameters
        self.graph_name = graph_analisis_context.graph_name

    def prepare(self):
        self.make_graph()

    def make_graph(self):
        query = f'''
            CALL gds.graph.project(
            '{self.graph_name}',
            '{self.graph_db_parameters.main_node_name}',
            {{
                {self.graph_db_parameters.main_rels_name}: {{
                    orientation: 'UNDIRECTED',
                    properties: '{self.graph_db_parameters.weight}'
                }}
            }}
        )
        '''
        self.connection.run(query)