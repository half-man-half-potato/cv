import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table

# Load data
url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

# Create df_table
df_table = df[['Client_ID', 'Employer', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df_table = df_table.sort_values(by='Client_ID').drop(columns=['Client_ID'])

# Create df_gantt
df_gantt = df[['Client_ID', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Duration', 'Employer']].drop_duplicates()
df_gantt = df_gantt.sort_values(by='Client_ID', ascending=False)

# Convert date columns for Gantt chart
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])

# Create Gantt chart
fig_gantt = px.timeline(
    df_gantt,
    x_start="Start_Date",
    x_end="End_Date",
    y="Client_Name_Full",
    color="Employer"
)

# Hide Y axis, legend, and title
fig_gantt.update_layout(
    showlegend=False,
    yaxis=dict(visible=False),
    title=None,
    margin=dict(l=0, r=0, t=0, b=0)
)

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    # Gantt chart div
    html.Div(
        dcc.Graph(figure=fig_gantt, config={"displayModeBar": False}),
        style={
            "position": "absolute",
            "left": "0px",
            "top": "0px",
            "width": "300px",
            "height": "600px"
        }
    ),
    # Table div
    html.Div(
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df_table.columns],
            data=df_table.to_dict("records"),
            style_table={"height": "600px", "overflowY": "auto"},
            style_cell={'textAlign': 'left'}
        ),
        style={
            "position": "absolute",
            "left": "400px",
            "top": "0px",
            "width": "850px",
            "height": "600px"
        }
    )
])
