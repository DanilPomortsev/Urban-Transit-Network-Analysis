from enum import Enum

import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.MetricCalculationContext import MetricCalculationContext


class Printer:
    def __init__(
            self,
            data,
            metric_calculation_context: MetricCalculationContext
    ):
        self.data = data
        self.metric_calculation_context = metric_calculation_context

    def plot_histogram(
            self,
            metric: Enum,
            title="Distribution of metric_value",
            xlabel="metric_value",
            ylabel="Frequency"
    ):
        metric_name = metric.value
        metric_values = [item[metric_name + "_value"] for item in self.data]

        df = pd.DataFrame({"metric_value": metric_values})

        fig = px.histogram(df, x="metric_value", title=title, labels={"metric_value": xlabel, "count": ylabel},
                           marginal="rug")  # marginal="rug" добавляет rug plot

        fig.show()

    def plot_heatmap_on_map(
            self,
            metric: Enum,
            resolution=10,
            colorscale='Viridis'
    ):
        latitudes = []
        longitudes = []
        metric_values = []
        metric_name = metric.value

        for item in range(len(self.data[metric_name + "_identity"])):
            try:
                parsed_point = self.data[metric_name + "_identity"][item].split(" ")
                lat, lon = parsed_point[1][1::], parsed_point[2][:-1:]
                latitudes.append(float(lat))
                longitudes.append(float(lon))
                metric_values.append(self.data[metric_name + "_value"][item])
            except ValueError:
                print(f"Skipping invalid identity")

        df = pd.DataFrame({
            "latitude": latitudes,
            "longitude": longitudes,
            "metric_value": metric_values
        })
        df['metric_value'] = df['metric_value'].fillna(0)

        lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
        lon_min, lon_max = df['longitude'].min(), df['longitude'].max()

        lon_edges = np.linspace(lon_min, lon_max, resolution + 1)
        lat_edges = np.linspace(lat_min, lat_max, resolution + 1)

        lon_centers = (lon_edges[:-1] + lon_edges[1:]) / 2
        lat_centers = (lat_edges[:-1] + lat_edges[1:]) / 2

        avg_values = np.empty((resolution, resolution))
        avg_values.fill(0)

        for i in range(resolution):
            for j in range(resolution):
                mask = (
                        (df['longitude'] >= lon_edges[i]) &
                        (df['longitude'] < lon_edges[i + 1]) &
                        (df['latitude'] >= lat_edges[j]) &
                        (df['latitude'] < lat_edges[j + 1])
                )

                cell_points = df[mask]

                if len(cell_points) > 0:
                    mean_value = cell_points["metric_value"].mean()
                    avg_values[j, i] = 0 if np.isnan(mean_value) or np.isinf(mean_value) else mean_value

        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=avg_values,
            x=lon_centers,
            y=lat_centers,
            colorscale=colorscale,
            colorbar=dict(title='Среднее значение метрики'),
            hoverinfo='x+y+z',
            name='Средние значения',
        ))

        fig.show()


class HeatMapMetrics(Enum):
    PAGE_RANK = 'page_rank'
    BEETWEENESSENS = 'beetweenessens'


class HistogramMetrics(Enum):
    PAGE_RANK = 'page_rank'
    BEETWEENESSENS = 'beetweenessens'
    DEGREE = 'degree'
    LEIDEN_MODULARITY = 'leiden_modularity'
    LOUVAIN_MODULARITY = 'louvain_modularity'
