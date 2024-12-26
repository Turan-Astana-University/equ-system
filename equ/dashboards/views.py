
import plotly.express as px
from django.shortcuts import render
import pandas as pd
from equipments.models import Equipment, EquipmentType


def dashboard_view(request):
    # Пример данных

    queryset = Equipment.objects.select_related('category ').all()
    data = Equipment.objects.values('title', 'location', 'category__title')
    df = pd.DataFrame(data)
    print(df.columns)
    # Построение графика с Plotly
    fig = px.pie(
        df,
        names='category__title',  # Параметр для названия категорий
        title="Круговая диаграмма: Категории и Количество"  # Заголовок
    )

    # Настройка отображения процентов и меток
    fig.update_traces(textinfo='percent+label')

    # Отображение диаграммы
    graph_json = fig.to_json()  # Конвертируем график в JSON

    # Передача в шаблон
    return render(request, 'dashboards/dashboard.html', {'graph_json': graph_json})