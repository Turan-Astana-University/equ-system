
import plotly.express as px
from django.shortcuts import render
import pandas as pd
from equipments.models import Equipment, EquipmentType


def dashboard_view(request):
    print(request, "SDSAJUDFBSAKJD")
    data = Equipment.objects.values('title', 'location', 'category__title')
    df = pd.DataFrame(data)
    fig = px.pie(
        df,
        names='category__title',
        title="Круговая диаграмма: Категории и Количество"
    )

    fig.update_traces(textinfo='percent+label')
    graph_json = fig.to_json()

    return render(request, 'dashboards/dashboard.html', {'graph_json': graph_json})