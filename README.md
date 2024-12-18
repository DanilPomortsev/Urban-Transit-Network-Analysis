# Кластеризация дорожных сетей и автобусных остановок

## Возможности:

1. Кластеризация дорожных сетей произвольных российских городов
2. Кластеризация автобусных остановок Санкт-Петербурга

## Необходимо:

1. Установить зависимости `pip install -r requirements.txt`.
2. Установить Neo4j Desktop.
3. Создать БД и вести имя, пароль, порт. Параметры можно посмотреть в `neo4j_connection.py`.
4. Установить плагин graph-data-science для работы `community_detection.py`. Плагин можно установить или через интерфейс
   Neo4j Desktop, или вручную, скачав совместимый с версией базы данных
   [плагин](https://github.com/neo4j/graph-data-science/releases) и поместив его в папку с плагинами
   созданного проекта. Также в файле конфигурации `neo4j.conf` проекта необходимо установить параметр со следующими
   значениями `dbms.security.procedures.unrestricted=jwt.security.*, apoc.*, gds.*`
5. Запустить `__main__.py`. Будут созданы графы дорог и сети автобусных остановок, а затем они будут кластеризованы с
   помощью алгоритмов Leiden и Louvain.

## Создание графов дорог и сети автобусных остановок:

Для создания графов дорог и сети автобусных остановок могут быть использованы классы `RoadGraphDBManager`
и `BusGraphDBManager` соответственно. Они имеют общую функцию `GraphDBManager#update_db` для добавления графа в Neo4j

`RoadGraphDBManager` берет данные из OpenStreetMap с помощью библиотеки osmnx. `BusGraphDBManager` берет данные
из https://kudikina.ru. С этого сайта есть возможность получать данные о дорожных сетях более чем 200
городов, что и реализовано в `parser.py`.

Подробнее о получаемых данных автобусной сети:

- Вершины - остановки. Включает географическое положение остановки (могут быть не
  точными - если информацию получить не удалось, то в таком случае данные будут приближенными и узел будет
  иметь `isCoordinateApproximate = True`), название остановки, список автобусных маршрутов в которых включена
  остановка;
- Связи - маршруты между соседними остановками внутри одного автобусного маршрута (название маршрута, длительность
  перемещения между соединяемыми остановками).

## Кластеризация дорог и сети автобусных остановок:

Для кластеризации могут быть использованы `Louvain` и `Leiden` классы, реализующие соответсвующее алгоритмы с помощью
Neo4j. Они имеют общий метод `CommunityDetection#detect_communities`, с помощью которого можно выполнить кластеризацию.
В методе можно указать название, параметр кластеризации, название вершин и связей графа дорог или автобусной сети.

В итоге к узлам добавится параметр, который будет определяться принадлежность к определенному кластеру. И также
выведется модулярность кластеризации.

## Визуализация данных

Можно визуализировать результаты с помощью Neo4j Bloom, расположив точки в географическом положении и
раскрасив их в соответствии с группами кластеризации.

## Источники информации используемые при разработке:

1. https://neo4j.com/docs/python-manual/current/
2. https://neo4j.com/docs
3. https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/
4. https://neo4j.com/docs/graph-data-science/current/algorithms/leiden/
5. https://en.wikipedia.org/wiki/Louvain_method
6. https://proproprogs.ru/ml/ml-aglomerativnaya-ierarhicheskaya-klasterizaciya-dendogramma
