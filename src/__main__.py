from src.context.AnalisisContext import AnalisContext
from src.AnalisisManager import AnalisisManager

if __name__ == "__main__":
    analis_context = AnalisContext(ru_city_name="Санкт-Петербург")
    analis_manager = AnalisisManager(analis_context)
    analis_manager.process()