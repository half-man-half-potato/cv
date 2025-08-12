import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table

url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

df_table = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df_table = df_table.sort_values(by='Client_Order').drop(columns=['Client_Order'])

df_gantt = df[['Client_ID', 'Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates()
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt = df_gantt.sort_values(by='Client_Order', ascending=False)

fig_gantt = px.timeline(
    df_gantt,
    x_start="Start_Date",
    x_end="End_Date",
    y="Client_Name_Full",
    color="Employer",
    color_discrete_sequence=["darkgray", "gainsboro"]
)

fig_gantt.update_layout(
    showlegend=False,
    yaxis=dict(visible=False),
    title=None,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor='white'
)

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        dcc.Graph(figure=fig_gantt, config={"displayModeBar": False}),
        style={
            "position": "absolute",
            "left": "20px",
            "top": "30px",
            "width": "300px",
            "height": "435px"
        }
    ),
    html.Div(
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df_table.columns],
            data=df_table.to_dict("records"),
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={'textAlign': 'left'}
        ),
        style={
            "position": "absolute",
            "left": "330px",
            "top": "0px",
            "width": "850px",
            "height": "500px"
        }
    )
])
