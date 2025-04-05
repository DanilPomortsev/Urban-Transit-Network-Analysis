from enums.HeatMapMetrics import HeatMapMetrics
from enums.HistogramMetrics import HistogramMetrics

"""
    Контекст для отрисовки графиков о метриках сетей
"""


class PrintGraphAnalisContext:
    def __init__(
            self,
            heat_map_metrics_list: [HeatMapMetrics] = None,
            histogram_map_metrics_list: [HistogramMetrics] = None,
            mesh_size: int = 100
    ):
        self.heat_map_metrics_list = heat_map_metrics_list if heat_map_metrics_list is not None \
            else list(HeatMapMetrics.__members__.values())
        self.histogram_map_metrics_list = histogram_map_metrics_list if histogram_map_metrics_list is not None \
            else list(HistogramMetrics.__members__.values())
        self.mesh_size = mesh_size
