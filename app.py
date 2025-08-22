import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output
import random

df = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv")

df_clients = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates().sort_values(by='Client_Order')
df_clients_style = [
    {"if": {"state": "active"}, "backgroundColor": "lightblue"},
    {"if": {"state": "selected", "row_index": "odd"}, "backgroundColor": "whitesmoke", "border": "none"},
    {"if": {"state": "selected", "row_index": "even"}, "backgroundColor": "white", "border": "none"},
    {"if": {"row_index": "odd"}, "backgroundColor": "whitesmoke"},
]

df_gantt = df[['Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates().sort_values(by='Client_Order', ascending=False)
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt['color'] = df_gantt['Employer'].map({'EPAM Systems': 'darkgray', 'Ernst & Young': 'gainsboro'})

df_roles = df[['Role', 'Role_Font_Size']].drop_duplicates().sort_values(by='Role')
df_roles_style = [
    {
        "if": {"filter_query": f'{{Role}} = "{row["Role"]}"'},
        "fontSize": f'{row["Role_Font_Size"]}px'
    }
    for _, row in df_roles.iterrows()
]

df_achievements = df[['Achievement', 'Achievement_Priority']].drop_duplicates().sort_values(by='Achievement_Priority')

df_tasks = df[['Task', 'Task_Priority']].drop_duplicates().sort_values(by='Task_Priority')








# Filter rows with non-empty Tool info and remove duplicates
df_tools = df[["Tool", "Tool_Type", "Tool_Size"]].drop_duplicates()
tool_type_colors = {
    "BI": "rgb(200,82,0)",
    "data": "rgb(245,156,60)",
    "language": "rgb(112,112,112)",
    "misc": "rgb(183,183,183)"
}
tool_type_colors_2 = {
    "BI": "rgb(249,234,224)",
    "data": "rgb(255,246,236)",
    "language": "rgb(241,241,241)",
    "misc": "rgb(248,248,248)"
}
df_tools["Color"] = df_tools["Tool_Type"].map(tool_type_colors).fillna("black")

size_min, size_max = 10, 24
tool_sizes = df_tools["Tool_Size"]
size_scaled = ((tool_sizes - tool_sizes.min()) / (tool_sizes.max() - tool_sizes.min()) * (size_max - size_min)) + size_min
tools_count = len(df_tools)
random.seed(42)
x_gap = 15
y_gap = 5
def rand_custom_x():
    return random.gauss(0.5, 0.15)
def rand_custom_y():
    return random.gauss(0.5, 0.15)
df_tools["x_pos"] = [rand_custom_x() for _ in range(tools_count)]
df_tools["y_pos"] = [rand_custom_y() for _ in range(tools_count)]
df_tools["len"] = df_tools["Tool"].str.len()

counter2 = 0
while 1 == 1 :
    counter = 0
    for i in range(tools_count):
        for j in range(tools_count):
            if  i > j:
                i_x_loc = df_tools.iloc[i, 4]
                i_y_loc = df_tools.iloc[i, 5]
                j_x_loc = df_tools.iloc[j, 4]
                j_y_loc = df_tools.iloc[j, 5]
                if abs(i_x_loc - j_x_loc) < x_gap/100 and abs(i_y_loc - j_y_loc) < y_gap/100:
                    df_tools.iloc[i, 4] = rand_custom_x()
                    df_tools.iloc[i, 5] = rand_custom_y()
                    counter += 1
    counter2 += 1
    if counter == 0:
        break
print(counter2)

df_tools.to_csv("word_cloud_coordinates.csv", index=False)

###################

def create_wordcloud(selected_client_order=None):
    df_plot = df_tools.copy()
    if selected_client_order is not None:
        related_tools = df[df["Client_Order"] == selected_client_order]["Tool"].drop_duplicates()
        print(f'{related_tools}')
        print(f'{type(related_tools)}')


        # df_plot.loc[df_plot['Client_Order'] == selected_client_order, 'color'] = 'dimgray'
        # pd.DataFrame({"Task": filtered_tasks}).to_dict("records"),  # 5 - UNDERSTAND THIS

    fig = px.scatter(
        df_plot,
        x=df_plot["x_pos"],
        y=df_plot["y_pos"],
        text="Tool"
    )
    fig.update_traces(
        mode="text",
        textposition="middle center",
        textfont_size=size_scaled,
        textfont_color=df_plot["Color"],
        hovertemplate="x_pos: %{x}<br>y_pos: %{y}",
        customdata=df_plot[["Tool_Type", "Tool_Size"]]
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='white',
        height=600,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig.update_yaxes(visible=False)
    fig.update_xaxes(visible=False)

    return fig
#####################

def create_gantt(selected_client_order=None, selected_client_row=None):
    df_plot = df_gantt.copy()
    if selected_client_order is not None:
        df_plot.loc[df_plot['Client_Order'] == selected_client_order, 'color'] = 'dimgray'

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
        if selected_client_order is not None and i == len(category_order) - selected_client_row - 1:
            shapes.append({
                "type": "rect",
                "xref": "paper",
                "yref": "y",
                "x0": 0,
                "x1": 1,
                "y0": i - 0.5,
                "y1": i + 0.5,
                "fillcolor": "rgba(173, 216, 230, 1)",
                "layer": "below",
                "line": {"width": 0}
            })
        elif i % 2 == 0:
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

app.layout = html.Div([
    html.Div(
        dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False, "displaylogo": False}),
        style={"position": "absolute", "left": "20px", "top": "30px", "width": "300px", "height": "446px", "borderTop": "1px solid lightgray", "zIndex": 2}
    ),
    html.Div(
        "Timeline / Client",
        style={"position": "absolute", "left": "20px", "top":  "0px","backgroundColor": "white", "height": "30px",
               "padding": "5px", "fontSize": "12px", "fontWeight": "bold", "color": "gray", "zIndex": 1}
    ),
    html.Div(
        dash_table.DataTable(
            id="projects-table",
            data=df_clients.to_dict("records"),
            columns=[
                {"name": "Country", "id": "Country"},
                {"name": "Client", "id": "Client_Name_Full"},
                {"name": "Project / Product", "id": "Project"},
                {"name": "Client_Order", "id": "Client_Order", "hideable": True}
            ],
            hidden_columns=["Client_Order"],
            style_table={"height": "500px", "overflowY": "auto"},
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            style_data_conditional=df_clients_style,
            css=[{"selector": ".show-hide", "rule": "display: none"}],
        ),
        style={"position": "absolute", "left": "305px", "top": "0px", "width": "850px", "height": "500px", "zIndex": 3}
    ),
    html.Div(
        dash_table.DataTable(
            id="roles-table",
            data=df_roles.to_dict("records"),
            columns=[{"name": "Role", "id": "Role"}],
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            style_data_conditional=df_roles_style,
            style_table={"overflowY": "auto", "height": "500px"},
        ),
        style={"position": "absolute", "left": "1180px", "top": "0px", "width": "300px", "height": "500px", "zIndex": 2}
    ),
    html.Div(
        dash_table.DataTable(
            id="achievements-table",
            data=df_achievements.to_dict("records"),
            columns=[{"name": "Achievement", "id": "Achievement"}],
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            # style_data_conditional=,
            style_table={"overflowY": "auto", "height": "180px"},
            fixed_rows={'headers': True},
        ),
        style={"position": "absolute", "left": "20px", "top": "500px", "width": "650px", "height": "180px", "zIndex": 2}
    ),
    html.Div(
        dash_table.DataTable(
            id="tasks-table",
            data=df_tasks.to_dict("records"),
            columns=[{"name": "Task", "id": "Task"}],
            style_cell={"textAlign": "left", "border": "none"},
            style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "gray", "backgroundColor": "white"},
            # style_data_conditional=,
            style_table={"overflowY": "auto", "height": "180px"},
            fixed_rows={'headers': True},
        ),
        style={"position": "absolute", "left": "20px", "top": "700px", "width": "650px", "height": "180px", "zIndex": 2}
    ),

#################3
    html.Div(
        dcc.Graph(id="word-cloud", figure=create_wordcloud(), config={"displayModeBar": False, "displaylogo": False}),
        style={"position": "absolute", "left": "700px", "top": "500px", "width": "800px", "height": "380px", "borderTop": "1px solid lightgray", "zIndex": 2}
    ),

##################
    html.Div(
        id="outside-click",
        style={"position": "absolute", "left": "0px", "top": "0px", "width": "90vw", "height": "90vh", "backgroundColor": "lavender", "zIndex": 0}
    )
])

# active_cell changes in the Projects table
@app.callback(
    Output("gantt-chart", "figure"), # 1. update Gantt
    Output("projects-table", "style_data_conditional"), # 2. update Projects
    Output("roles-table", "style_data_conditional"), # 3. update Roles
    Output("achievements-table", "data"), # 4. update Achievements
    Output("tasks-table", "data"), # 5. update Tasks
    Output("word-cloud", "figure"),  # 6. update Word cloud
    Input("projects-table", "active_cell"),
    Input("projects-table", "data")
)
def projects_table_callback(active_cell, data):
    
    # default outputs (no active_cell in Projects table)
    if active_cell is None:
        return (create_gantt(), # 1
                df_clients_style, # 2
                df_roles_style, # 3
                df_achievements.to_dict("records"), # 4
                df_tasks.to_dict("records"), # 5
                create_wordcloud()) # 6

    active_cell_row = active_cell["row"]
    selected_client_order = data[active_cell_row]["Client_Order"]

    df_clients_style_conditional = [{"if": {"row_index": active_cell_row}, "backgroundColor": "lightblue"}]

    related_roles = df[df["Client_Order"] == selected_client_order]["Role"].unique()
    df_roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{role}"'}, "backgroundColor": "lightblue"} for role in related_roles]

    filtered_achievements = df[df["Client_Order"] == selected_client_order]["Achievement"].drop_duplicates().sort_values()

    filtered_tasks = df[df["Client_Order"] == selected_client_order]["Task"].drop_duplicates().sort_values()

    print(filtered_tasks)
    print(type(filtered_tasks))

    # conditional outputs (active_cell in Projects table)
    return (create_gantt(selected_client_order=selected_client_order, selected_client_row=active_cell_row), # 1
            df_clients_style + df_clients_style_conditional, # 2
            df_roles_style + df_roles_style_conditional, # 3
            pd.DataFrame({"Achievement": filtered_achievements}).to_dict("records"), # 4 - UNDERSTAND THIS
            pd.DataFrame({"Task": filtered_tasks}).to_dict("records"), # 5 - UNDERSTAND THIS
            create_wordcloud(selected_client_order=selected_client_order)) # 6

@app.callback(
    Output("projects-table", "active_cell"),
    Input("outside-click", "n_clicks"),
    prevent_initial_call=True
)
def clear_active_cell(n_clicks):
    return None

