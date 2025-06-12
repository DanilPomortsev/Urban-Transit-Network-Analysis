from context.GraphAnalisContext import GraphAnalisContext
from enums.GraphTypes import GraphTypes
import AnalisisManager
from context import AnalisisContext

analisis_con = AnalisisContext.AnalisContext(
    ru_city_name="Санкт-Петербург",
    graph_analis_context=[GraphAnalisContext(
        graph_type=GraphTypes.BUS_GRAPH,
        need_create_graph=False,
        need_prepare_data=False,
        need_calculate_and_print_data=True,
    )]
)
am = AnalisisManager.AnalisisManager()
am.process(analisis_con)
