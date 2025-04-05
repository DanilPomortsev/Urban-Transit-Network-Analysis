import random

from deep_translator import GoogleTranslator
from graph_db_manager import RoadGraphDBManager,\
                             BusGraphDBManager, \
                             TrolleyGraphDBManager,\
                             TramGraphDBManager, \
                             MiniBusGraphDBManager, \
                             RoadBuildingsDbManager
from Printer import Printer, HistogramMetrics
from src.MetricCalculationContext import MetricCalculationContext
from src.MetricDataCalculator import MetricDataCalculator
from src.MetricDataPreparer import MetricDataPreparer

if __name__ == "__main__":
    ru_city_name = "Пермь"
    all_types = [
        {
            "name": "Road",
            "dbManagerConstructor": RoadGraphDBManager,
        }
    ]
    translator = GoogleTranslator(source='ru', target='en')
    metric_context = MetricCalculationContext(
        need_leiden_community_id=False,
        need_louvain_community_id=False,
        need_leiden_modulariry=False,
        need_louvain_modulariry=False,
        need_betweenessens=True,
        need_page_rank=False,
        need_degree=False
    )

    for type_graph in all_types:
        name = type_graph["name"]
        db_manager_constructor = type_graph["dbManagerConstructor"]

        db_manager = db_manager_constructor()
        db_manager.update_db(ru_city_name)

        city_name = translator.translate(ru_city_name).replace(" ", "")
        metric_data_preparer = MetricDataPreparer(metric_context, "somesome" + str(random.random()), db_manager)
        prepare_result = metric_data_preparer.prepare_metrics()
        metric_data_calculator = MetricDataCalculator(metric_context, db_manager)
        data = metric_data_calculator.calculate_data(prepare_result)

        printer = Printer(data, metric_context)
        printer.plot_heatmap_on_map(HistogramMetrics.BEETWEENESSENS)