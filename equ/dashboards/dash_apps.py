import dash
from dash import dcc, html
import plotly.express as px
from django_plotly_dash import DjangoDash
import pandas as pd

# Пример данных
df = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Values": [10, 20, 30, 40]
})

# Создаем приложение Dash
app = DjangoDash('DashboardApp')  # Имя приложения

# Построение графика
fig = px.bar(df, x="Category", y="Values", title="Пример графика")

# Определяем интерфейс Dash
app.layout = html.Div([
    html.H1("Интерактивный дашборд", style={"textAlign": "center"}),
    dcc.Graph(id='example-graph', figure=fig),
    html.P("Выберите категорию для фильтрации:"),
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': cat, 'value': cat} for cat in df['Category']],
        value='A'
    ),
    dcc.Graph(id='filtered-graph')
])

# Добавляем интерактивность
@app.callback(
    dash.dependencies.Output('filtered-graph', 'figure'),
    [dash.dependencies.Input('category-dropdown', 'value')]
)
def update_graph(selected_category):
    filtered_df = df[df['Category'] == selected_category]
    fig = px.bar(filtered_df, x="Category", y="Values", title=f"График для категории {selected_category}")
    return fig