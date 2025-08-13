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
        if i % 2 == 1:
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
    return fig

app = Dash(__name__)

# base styles used initially AND reused in callback
BASE_STYLE = [
    {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"},
    # Blue active cell (override Plotly's default red) — set all four borders explicitly
    {
        "if": {"state": "active"},
        "backgroundColor": "lightblue",
        "border": "0px solid blue",
        "borderTop": "0px solid blue",
        "borderRight": "0px solid blue",
        "borderBottom": "0px solid blue",
        "borderLeft": "0px solid blue",
    },
]

app.layout = html.Div([
    html.Div(
        dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False, "displaylogo": False}),
        style={"position": "absolute", "left": "20px", "top": "30px", "width": "300px", "height": "435px"}
    ),
    html.Div(
        dash_table.DataTable(
            id="data-table",
            columns=[
                {
                    "name": "Client" if col == "Client_Name_Full"
                    else "Project / Product" if col == "Project"
                    else col,
                    "id": col,
                }
                for col in df_table.columns
            ],
            data=df_table.to_dict("records"),
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={
                "textAlign": "left",
                "border": "none"  # remove all borders
            },
            style_header={
                "borderBottom": "1px solid lightgray",  # header bottom border only
                "fontWeight": "bold",
                "color": "gray",
                "backgroundColor": "white"
            },
            hidden_columns=["Client_Order"],
            css=[{"selector": ".show-hide", "rule": "display: none"}],
            style_data_conditional=BASE_STYLE  # initial (no row selection yet)
        ),
        style={"position": "absolute", "left": "330px", "top": "0px", "width": "850px", "height": "500px"}
    )
])

@app.callback(
    Output("gantt-chart", "figure"),
    Output("data-table", "style_data_conditional"),
    Input("data-table", "active_cell"),
    Input("data-table", "data")
)
def update_gantt_and_highlight(active_cell, table_data):
    # start with base banding + blue active cell rule
    style_data_conditional = BASE_STYLE.copy()

    if active_cell is None:
        return create_gantt(), style_data_conditional

    # whole-row highlight to match
    selected_row_idx = active_cell["row"]
    style_data_conditional.append({
        "if": {"row_index": selected_row_idx},
        "backgroundColor": "lightblue"
    })

    client_order_value = table_data[selected_row_idx]["Client_Order"]
    return create_gantt(highlight_client_order=client_order_value), style_data_conditional
