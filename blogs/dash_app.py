import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from django_plotly_dash import DjangoDash

# Sample data - replace with your actual data
data = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Value": [10, 20, 30, 40]
})

# Create the Dash app
app = DjangoDash('Analytics')

# Build the layout of the app
app.layout = html.Div([
    html.H1("Analytics Dashboard"),
    dcc.Graph(
        id="bar-chart",
        figure=px.bar(data, x="Category", y="Value", title="Category vs Value")
    )
])

