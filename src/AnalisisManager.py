import random

from src.context.AnalisisContext import AnalisContext
from src.data.calculator.MetricDataCalculator import MetricDataCalculator
from src.data.preparer.MetricDataPreparer import MetricDataPreparer
from src.graphics.Printer import Printer
"""
    Класс ответственный за анализ сетей
"""


class AnalisisManager:
    def __init__(self, analis_context: AnalisContext):
        self.analis_context = analis_context

    def process(self):
        ru_city_name = self.analis_context.ru_city_name

        for graph_analis_context in self.analis_context.graph_analis_context:
            db_manager_constructor = graph_analis_context.graph_type.value
            metric_context = graph_analis_context.metric_calculation_context

            db_manager = db_manager_constructor()
            db_manager.update_db(ru_city_name)

            prepare_result = None
            if graph_analis_context.need_prepare_data:
                new_graph_name = graph_analis_context.new_graph_name if graph_analis_context.new_graph_name is not None \
                    else "some" + str(random.random())
                metric_data_preparer = MetricDataPreparer(
                    metric_context,
                    new_graph_name,
                    db_manager
                )
                prepare_result = metric_data_preparer.prepare_metrics()

            if graph_analis_context.need_calculate_and_print_data:
                metric_data_calculator = MetricDataCalculator(
                    metric_context,
                    db_manager
                )
                data = metric_data_calculator.calculate_data(prepare_result)

                printer = Printer(
                    data,
                    metric_context
                )
                printer.print_graphics(graph_analis_context.print_graph_analis_context)
