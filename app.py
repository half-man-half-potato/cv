import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output

url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

df_table = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df_table = df_table.sort_values(by='Client_Order')

df_gantt = df[['Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates()
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt = df_gantt.sort_values(by='Client_Order', ascending=False)
df_gantt['color'] = df_gantt['Employer'].map({'EPAM Systems': 'darkgray', 'Ernst & Young': 'gainsboro'})

# <--  INCLUDE Role_Size here  -->
df_roles = (
    df[['Role', 'Role_Size']]
    .drop_duplicates()
    .sort_values(by='Role')
)

# Linear font mapping helper
min_size = df_roles['Role_Size'].min()
max_size = df_roles['Role_Size'].max()

def font_from_role_size(value):
    norm = (value - min_size) / (max_size - min_size)
    level = int(norm * 4 + 0.5)
    return 10 + level  # 10...14

role_style = [
    {
        "if": {"filter_query": f'{{Role}} = "{role}"'},
        "fontSize": f"{font_from_role_size(size)}px"
    }
    for role, size in df_roles[['Role', 'Role_Size']].values
]

style_base = [
    {"if": {"state": "active"}, "backgroundColor": "lightblue"},
    {"if": {"state": "selected", "row_index": "odd"}, "backgroundColor": "whitesmoke", "border": "none"},
    {"if": {"state": "selected", "row_index": "even"}, "backgroundColor": "white", "border": "none"},
    {"if": {"row_index": "odd"}, "backgroundColor": "whitesmoke"},
]

def create_gantt(selected_client_order=None):
    df_plot = df_gantt.copy()
    if selected_client_order is not None:
        df_plot.loc[df_plot['Client_Order'] == selected_client_order, 'color'] = 'dimgray'
    names_reversed = df_plot["Client_Name_Full"].tolist()[::-1]
    category_order = list(dict.fromkeys(names_reversed))
    fig = px.timeline(
        df_plot, x_start="Start_Date", x_end="End_Date", y="Client_Name_Full",
        color="color", color_discrete_map="identity",
        category_orders={"Client_Name_Full": category_order}
    )
    shapes = []
    for i in range(len(category_order)):
        if i % 2 == 0:
            shapes.append({
                "type": "rect","xref": "paper","yref": "y", "x0": 0,"x1": 1,
                "y0": i - 0.5,"y1": i + 0.5,
                "fillcolor": "rgba(240, 240, 240, 0.5)","layer": "below","line": {"width": 0}
            })
    fig.update_layout(showlegend=False, title=None, margin=dict(l=0, r=0, t=0, b=0),
                      plot_bgcolor='white', shapes=shapes)
    fig.update_yaxes(visible=False)
    fig.update_xaxes(
        tickvals=[pd.Timestamp(f"{y}-01-01") for y in range(2010, 2026, 5)],
        ticktext=[str(y) for y in range(2010, 2026, 5)],
        tickangle=90, color='gray', tickfont=dict(size=10),
        range=[pd.Timestamp("2009-10-01"), pd.Timestamp("2025-12-31")]
    )
    return fig

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False, "displaylogo": False}),
        style={"position": "absolute", "left": "20px", "top": "30px", "width": "300px", "height": "446px", "zIndex": 1}
    ),
    html.Div(
        dash_table.DataTable(
            id="data-table",
            data=df_table.to_dict("records"),
            columns=[
                {"name": "Country", "id": "Country"},
                {"name": "Client", "id": "Client_Name_Full"},
                {"name": "Project / Product", "id": "Project"},
                {"name": "Client_Order", "id": "Client_Order", "hideable": True},
            ],
            hidden_columns=["Client_Order"],
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            style_data_conditional=style_base,
            css=[{"selector": ".show-hide", "rule": "display: none"}],
        ),
        style={"position": "absolute", "left": "305px", "top": "0px", "width": "850px", "height": "500px", "zIndex": 2}
    ),
    html.Div(
        dash_table.DataTable(
            id="role-table",
            data=df_roles.to_dict("records"),
            columns=[
                {"name": "Role", "id": "Role"},
                # keep Role_Size in the table so we can reference it for styling
                {"name": "Role_Size", "id": "Role_Size"}
            ],
            hidden_columns=["Role_Size"],
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            style_data_conditional=role_style,
            css=[{"selector": ".dash-spreadsheet-menu", "rule": "display: none"}],
        ),
        style={"position": "absolute", "left": "1180px", "top": "0px", "width": "300px", "height": "500px", "zIndex": 2}
    ),

    html.Div(
        id="outside-click",
        style={"position": "absolute", "left": "0px", "top": "0px",
               "width": "90vw", "height": "90vh", "backgroundColor": "lavender", "zIndex": 0}
    )
])

@app.callback(
    Output("gantt-chart", "figure"),
    Output("data-table", "style_data_conditional"),
    Input("data-table", "active_cell"),
    Input("data-table", "data")
)
def update_gantt_and_table(active_cell, table_data):
    styles = style_base.copy()
    if active_cell is None:
        return create_gantt(), styles
    row = active_cell["row"]
    styles.append({"if": {"row_index": row}, "backgroundColor": "lightblue"})
    return create_gantt(selected_client_order=table_data[row]["Client_Order"]), styles

@app.callback(
    Output("role-table", "style_data_conditional"),
    Input("data-table", "active_cell"),
    Input("data-table", "data")
)
def update_roles(active_cell, table_rows):
    styles = role_style.copy()   # <— start with the font‐size rules

    if not active_cell:
        return styles

    row = active_cell["row"]
    client_order = table_rows[row]["Client_Order"]
    roles = df[df["Client_Order"] == client_order]["Role"].unique()

    # Add highlight rules *on top* of font-size rules:
    for role in roles:
        styles.append({
            "if": {"filter_query": f'{{Role}} = \"{role}\"'},
            "backgroundColor": "lightblue"
        })

    return styles

@app.callback(
    Output("data-table", "active_cell"),
    Input("outside-click", "n_clicks"),
    prevent_initial_call=True
)
def clear_active_cell(n_clicks):
    return None

if __name__ == "__main__":
    app.run(debug=True)
