
import plotly.express as px
from django.shortcuts import render
import pandas as pd

def dashboard_view(request):
    # Пример данных
    data = {
        "Category": ["A", "B", "C", "D"],
        "Values": [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)

    # Построение графика с Plotly
    fig = px.bar(df, x="Category", y="Values", title="Пример графика")
    graph_json = fig.to_json()  # Конвертируем график в JSON

    # Передача в шаблон
    return render(request, 'dashboards/dashboard.html', {'graph_json': graph_json})