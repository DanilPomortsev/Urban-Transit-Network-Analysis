from context.MetricCalculationContext import MetricCalculationContext
from database.GraphDbManager import GraphDBManager
from database.MetricsDistribution import DegreeDistribution, BetweennessDistribution, PageRankDistribution
"""
    Класс вычисляющий метрики сетей(берёт уже записанные метрики из бд или вычисляет не сложные)
"""


class MetricDataCalculator:
    def __init__(
            self,
            metric_calculation_context: MetricCalculationContext,
            db_manager: GraphDBManager
    ):
        self.metric_calculation_context = metric_calculation_context
        self.db_manager = db_manager
        self.degree_distibution_calculator = None
        self.betweenessens_distribution_calculator = None
        self.page_rank_distribution_calculator = None
        if metric_calculation_context.need_degree:
            self.degree_distibution_calculator = DegreeDistribution(self.db_manager)
        if metric_calculation_context.need_betweenessens:
            self.betweenessens_distribution_calculator = BetweennessDistribution(self.db_manager)
        if metric_calculation_context.need_page_rank:
            self.page_rank_distribution_calculator = PageRankDistribution(self.db_manager)

    def calculate_data(self, prepare_result):
        degree_distribution = {}
        if self.degree_distibution_calculator is not None:
            degree_distirbution_data = self.degree_distibution_calculator.calculate_distribution()
            degree_distribution = {"degree_value": [item[1] for item in degree_distirbution_data] }

        betweenessens_distibution = {}
        if self.betweenessens_distribution_calculator is not None:
            betweenessens_distirbution_data = self.betweenessens_distribution_calculator.calculate_distribution()
            betweenessens_distibution = {
                "beetweenessens_identity": [item[0] for item in betweenessens_distirbution_data],
                "beetweenessens_value": [item[1] for item in betweenessens_distirbution_data],
            }

        page_rank_distibution = {}
        if self.page_rank_distribution_calculator is not None:
            page_rank_distirbution_data = self.page_rank_distribution_calculator.calculate_distribution()
            page_rank_distibution = {
                "page_rank_identity": [item[0] for item in page_rank_distirbution_data],
                "page_rank_value": [item[1] for item in page_rank_distirbution_data],
            }
        return {**degree_distribution, **betweenessens_distibution, **page_rank_distibution, **prepare_result}
