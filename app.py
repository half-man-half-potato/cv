import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# URLs to the CSV files
CLIENTS_CSV = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/1_client.csv"
TASKS_CSV = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/2_task.csv"

# Load the CSVs into pandas DataFrames
clients_df = pd.read_csv(CLIENTS_CSV)
tasks_df = pd.read_csv(TASKS_CSV)

# Enforce primary/foreign key logic conceptually
# clients_df: 'client' is primary key
# tasks_df: 'task' is primary key, 'client' is foreign key referencing 'clients.client'

# Join the tables on the 'client' key
merged_df = tasks_df.merge(clients_df, on="client", how="left")

# Create a grouped DataFrame: count of tasks per client
task_counts = (
    merged_df.groupby("client_name_full")
    .agg(task_count=("task", "count"))
    .reset_index()
    .sort_values("task_count", ascending=True)
)

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Task Count per Client"),
    dcc.Graph(id="bar-chart"),
])

# Callback to render the horizontal bar chart
@app.callback(
    Output("bar-chart", "figure"),
    Input("bar-chart", "id")
)
def update_bar_chart(_):
    fig = px.bar(
        task_counts,
        x="task_count",
        y="client_name_full",
        orientation="h",
        labels={"task_count": "Number of Tasks", "client_name_full": "Client"},
        title="Tasks per Client"
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig