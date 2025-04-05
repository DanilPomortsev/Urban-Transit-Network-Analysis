from context.MetricCalculationContext import MetricCalculationContext
from context.GraphAnalisContext import GraphAnalisContext

"""
    Контекст для анализа сетей
"""


class AnalisContext:
    def __init__(
            self,
            ru_city_name: str = None,
            common_metric_calculation_context: MetricCalculationContext = MetricCalculationContext(),
            graph_analis_context: [GraphAnalisContext] = None
    ):
        if graph_analis_context is None:
            graph_analis_context = [GraphAnalisContext()]
        self.ru_city_name = ru_city_name
        self.common_metric_calculation_context = common_metric_calculation_context
        for item in graph_analis_context:
            if item.metric_calculation_context is None:
                item.metric_calculation_context = common_metric_calculation_context
        self.graph_analis_context = graph_analis_context
