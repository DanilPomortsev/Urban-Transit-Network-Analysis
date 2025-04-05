"""
    Контекст для вычисления метрик сетей
"""


class MetricCalculationContext:
    def __init__(
            self,
            need_leiden_community_id: bool = True,
            need_louvain_community_id: bool = True,
            need_leiden_modulariry: bool = True,
            need_louvain_modulariry: bool = True,
            need_betweenessens: bool = True,
            need_page_rank: bool = True,
            need_degree: bool = True
    ):
        self.need_leiden_community_id = need_leiden_community_id
        self.need_louvain_community_id = need_louvain_community_id
        self.need_leiden_modulariry = need_leiden_modulariry
        self.need_louvain_modulariry = need_louvain_modulariry
        self.need_betweenessens = need_betweenessens
        self.need_page_rank = need_page_rank
        self.need_degree = need_degree
