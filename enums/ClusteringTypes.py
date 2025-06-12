from enum import Enum
"""
    Список лгоритмов кластеризации с названиями для отрисовки в Heat Map
"""


class ClusteringTypes(Enum):
    LEIDEN = 'leiden'
    LOUVAIN = 'louvain'
