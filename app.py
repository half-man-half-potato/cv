import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

df_table = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df_table = df_table.sort_values(by='Client_Order')

df_gantt = df[['Client_ID', 'Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates()
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt = df_gantt.sort_values(by='Client_Order', ascending=False)

employer_colors = {
    'EPAM Systems': 'darkgray',
    'Ernst & Young': 'gainsboro'
}
df_gantt['color'] = df_gantt['Employer'].map(employer_colors)

def create_gantt(highlight_client_order=None):
    df_plot = df_gantt.copy()

    if highlight_client_order is not None:
        df_plot.loc[df_plot['Client_Order'] == highlight_client_order, 'color'] = 'dimgray'

    names_reversed = df_plot["Client_Name_Full"].tolist()[::-1]
    category_order = list(dict.fromkeys(names_reversed))

    fig = px.timeline(
        df_plot,
        x_start="Start_Date",
        x_end="End_Date",
        y="Client_Name_Full",
        color="color",
        color_discrete_map="identity",
        category_orders={"Client_Name_Full": category_order}
    )

    shapes = []
    for i in range(len(category_order)):
        if i % 2 == 0:
            shapes.append({
                "type": "rect",
                "xref": "paper",
                "yref": "y",
                "x0": 0,
                "x1": 1,
                "y0": i - 0.5,
                "y1": i + 0.5,
                "fillcolor": "rgba(240, 240, 240, 0.5)",
                "layer": "below",
                "line": {"width": 0}
            })

    fig.update_layout(
        showlegend=False,
        title=None,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        shapes=shapes
    )

    fig.update_yaxes(visible=False)
    fig.update_xaxes(
        tickvals=[pd.Timestamp(f"{y}-01-01") for y in range(2010, 2026, 5)],
        ticktext=[str(y) for y in range(2010, 2026, 5)],
        tickangle=90,
        color='gray',
        tickfont=dict(size=10),
        range=[pd.Timestamp("2009-10-01"), pd.Timestamp("2025-12-31")]
    )

    return fig

app = Dash(__name__)

# Base styles for table
BASE_STYLE = [
    {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"},
    # Active cell override (blue)
    {
        "if": {"state": "active"},
        "backgroundColor": "lightblue",
        "border": "0px solid lightblue",
    },
    # Force selected/focused cell to have white background immediately
    {
        "if": {"state": "selected"},
        "backgroundColor": "white",
        "border": "none"
    },
]

# Additional CSS to eliminate lag/flicker
CUSTOM_CSS = [
    {"selector": "td.cell--active", "rule": "background-color: lightblue !important;"},
    {"selector": "td.focused", "rule": "background-color: lightblue !important;"}
]

app.layout = html.Div([
    html.Div(
        dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False, "displaylogo": False}),
        style={"position": "absolute", "left": "20px", "top": "30px", "width": "300px", "height": "446px", "zIndex": 1}
    ),
    html.Div(
        dash_table.DataTable(
            id="data-table",
            columns=[
                {"name": "Client", "id": "Client_Name_Full"},
                {"name": "Project / Product", "id": "Project"},
                {"name": "Country", "id": "Country"},
                {"name": "Client_Order", "id": "Client_Order", "hideable": True}
            ],
            hidden_columns=["Client_Order"],
            data=df_table.to_dict("records"),
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={"textAlign": "left", "border": "none"},
            style_header={
                "borderBottom": "1px solid lightgray",
                "fontWeight": "bold",
                "color": "gray",
                "backgroundColor": "white"
            },
            css=CUSTOM_CSS + [{"selector": ".show-hide", "rule": "display: none"}],
            style_data_conditional=BASE_STYLE
        ),
        style={"position": "absolute", "left": "305px", "top": "0px", "width": "850px", "height": "500px", "zIndex": 2}
    ),
    html.Div(
        id="outside-click",
        style={"display": "inline-block", "width": "90vw", "height": "90vh", "backgroundColor": "lavender"}
    )
])

@app.callback(
    Output("gantt-chart", "figure"),
    Output("data-table", "style_data_conditional"),
    Input("data-table", "active_cell"),
    Input("data-table", "data")
)
def update_gantt_and_highlight(active_cell, table_data):
    style_data_conditional = BASE_STYLE.copy()
    if active_cell is None:
        return create_gantt(), style_data_conditional
    selected_row_idx = active_cell["row"]
    style_data_conditional.append({"if": {"row_index": selected_row_idx}, "backgroundColor": "lightblue"})
    client_order_value = table_data[selected_row_idx]["Client_Order"]
    return create_gantt(highlight_client_order=client_order_value), style_data_conditional

@app.callback(
    Output("data-table", "active_cell"),
    Input("outside-click", "n_clicks"),
    prevent_initial_call=True
)
def clear_active_cell(n_clicks):
    return None
