from src.context.MetricCalculationContext import MetricCalculationContext
from src.context.PrintGraphAnalisContext import PrintGraphAnalisContext
from src.enums.GraphTypes import GraphTypes

"""
    Контекст для анализа сети конкретной сети
"""


class GraphAnalisContext:
    def __init__(
            self,
            metric_calculation_context: MetricCalculationContext = MetricCalculationContext(),
            print_graph_analis_context: PrintGraphAnalisContext = PrintGraphAnalisContext(),
            new_graph_name: str = None,
            graph_type: GraphTypes = GraphTypes.ROAD_GRAPH,
            need_prepare_data: bool = True,
            need_calculate_and_print_data: bool = True
    ):
        self.metric_calculation_context = metric_calculation_context
        self.new_graph_name = new_graph_name
        self.graph_type = graph_type
        self.need_prepare_data = need_prepare_data
        self.print_graph_analis_context = print_graph_analis_context
        self.need_calculate_and_print_data = need_calculate_and_print_data
