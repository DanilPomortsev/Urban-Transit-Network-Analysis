from enum import Enum


class HistogramMetrics(Enum):
    PAGE_RANK = 'page_rank'
    BEETWEENESSENS = 'beetweenessens'
    DEGREE = 'degree'
    LEIDEN_MODULARITY = 'leiden_modularity'
    LOUVAIN_MODULARITY = 'louvain_modularity'