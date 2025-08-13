import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

# Load CSV
url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

# Table dataframe (keep Client_Order for callbacks, but hide in UI)
df_table = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df_table = df_table.sort_values(by='Client_Order')

# Gantt dataframe
df_gantt = df[['Client_ID', 'Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates()
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt = df_gantt.sort_values(by='Client_Order', ascending=False)

# Define original colors
employer_colors = {
    employer: color
    for employer, color in zip(df_gantt['Employer'].unique(), ["darkgray", "gainsboro"])
}

# Function to create Gantt figure
def create_gantt(highlight_client_order=None):
    df_plot = df_gantt.copy()
    df_plot['color'] = df_plot['Employer'].map(employer_colors)

    if highlight_client_order is not None:
        df_plot.loc[df_plot['Client_Order'] == highlight_client_order, 'color'] = 'dimgray'

    fig = px.timeline(
        df_plot,
        x_start="Start_Date",
        x_end="End_Date",
        y="Client_Name_Full",
        color="color",
        color_discrete_map="identity",
        category_orders={
            "Client_Name_Full": df_plot["Client_Name_Full"].tolist()[::-1]  # reverse order
        }
    )

    fig.update_layout(
        showlegend=False,
        yaxis=dict(visible=False),
        title=None,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white'
    )
    return fig

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False}),
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
            id="data-table",
            columns=[
                {"name": col, "id": col, "hideable": True} if col == "Client_Order" else {"name": col, "id": col}
                for col in df_table.columns
            ],
            data=df_table.to_dict("records"),
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={'textAlign': 'left'},
            hidden_columns=["Client_Order"],
            css=[{"selector": ".show-hide", "rule": "display: none"}],
            style_data_conditional=[
                # Row banding first
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(248, 248, 248)"
                },
                # Active cell highlight last so it overrides
                {
                    "if": {"state": "active"},
                    "backgroundColor": "lightblue",
                    # "border": "1px solid red"
                }
            ]
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

# Callback for interactivity
@app.callback(
    Output("gantt-chart", "figure"),
    Input("data-table", "active_cell"),
    Input("data-table", "data")
)
def update_gantt(active_cell, table_data):
    if active_cell is None:
        return create_gantt()

    clicked_row = active_cell["row"]
    client_order_value = table_data[clicked_row]["Client_Order"]

    return create_gantt(highlight_client_order=client_order_value)
