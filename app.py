import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Input, Output, ctx
from dash.exceptions import PreventUpdate
import json # for logging


#########################################################################################################################################################
######################################################################### DATA ##########################################################################
#########################################################################################################################################################

# Bug: Gantt row banding disappears when clicking on othe views (except for Clients table)


# Sources # ToDo: optimize
df = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv")

df_coordinates = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/word_cloud_coordinates.csv") # coordinates for Word cloud items

df_role_to_achievement = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/role-achievement.csv")
df_role_to_task = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/role-task.csv")
df_role_to_tool = pd.read_csv("https://raw.githubusercontent.com/half-man-half-potato/cv/master/role-tool.csv")


# Clients table
df_clients = df[['Client_Order', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates().sort_values(by='Client_Order')
clients_style = [
    {"if": {"state": "active"}, "backgroundColor": "lightblue"},
    {"if": {"state": "selected", "row_index": "odd"}, "backgroundColor": "whitesmoke", "border": "none"},
    {"if": {"state": "selected", "row_index": "even"}, "backgroundColor": "white", "border": "none"},
    {"if": {"row_index": "odd"}, "backgroundColor": "whitesmoke"},
    {"if": {"column_id": "Country"}, "width": "50px"},
    {"if": {"column_id": "Client_Name_Full"}, "fontSize": "14px", "width": "250px"},
    {"if": {"column_id": "Project"}, "color": "rgb(85,85,85)", "width": "250px"},
    {"if": {"filter_query": f'{{Country}} = "Belarus"', "column_id": "Country"}, "color": "rgb(128,176,213)", "fontWeight": "bold", "fontSize": "11px"},
    {"if": {"filter_query": f'{{Country}} = "USA"', "column_id": "Country"}, "color": "rgb(61,106,152)", "fontWeight": "bold", "fontSize": "11px"},
]
clients_orders_list = df["Client_Order"].drop_duplicates().sort_values().tolist()


# Gantt
df_gantt = df[['Client_Order', 'Client_Name_Full', 'Start_Date', 'End_Date', 'Employer']].drop_duplicates().sort_values(by='Client_Order', ascending=False)
df_gantt['Start_Date'] = pd.to_datetime(df_gantt['Start_Date'])
df_gantt['End_Date'] = pd.to_datetime(df_gantt['End_Date'])
df_gantt['color'] = df_gantt['Employer'].map({'EPAM Systems': 'rgb(164,164,164)', 'Ernst & Young': 'rgb(205,205,205)'})

all_clients_orders = df[["Client_Order"]].drop_duplicates().sort_values(by='Client_Order', ascending=False).values.tolist()


# Roles table
df_roles = df[['Role', 'Role_Font_Size']].drop_duplicates().sort_values(by='Role')
roles_style = [
    {"if": {"filter_query": f'{{Role}} = "{row["Role"]}"'}, "fontSize": f'{row["Role_Font_Size"]}px'}
    for _, row in df_roles.iterrows()
]
roles_style += [
    {"if": {"state": "active"}, "backgroundColor": "lightblue"},
    {"if": {"state": "selected"}, "backgroundColor": "white", "border": "none"},
]


# Achievements table
df_achievements = df[['Achievement', 'Achievement_Priority']].drop_duplicates().sort_values(by='Achievement_Priority')


# Tasks table
df_tasks = df[['Task', 'Task_Priority']].drop_duplicates().sort_values(by='Task_Priority')


# Word clous
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
df_tools = df_tools.merge(df_coordinates, on="Tool", how="left")
size_min, size_max = 10, 24
tool_sizes = df_tools["Tool_Size"]
size_scaled = ((tool_sizes - tool_sizes.min()) / (tool_sizes.max() - tool_sizes.min()) * (size_max - size_min)) + size_min


#########################################################################################################################################################
###################################################################### FUNCTIONS ########################################################################
#########################################################################################################################################################


def create_wordcloud(selected_client_order=None, selected_role=None, selected_tool=None, selected_task=None, selected_achievement=None):
    # ToDo: increase font size by 1 for the selected tools? (don't change the default view)
    df_plot = df_tools.copy()

    # dim colors for the unrelated items (if any)
    if selected_client_order is not None: # if triggered by the User clicking on the Clients table
        related_tools = df[df["Client_Order"] == selected_client_order]["Tool"].drop_duplicates().tolist()
        df_plot["Color"] = df_plot.apply(
            lambda row:
            tool_type_colors[row["Tool_Type"]] if row["Tool"] in related_tools
            else
            tool_type_colors_2[row["Tool_Type"]],
            axis=1
        )
    elif selected_role is not None: # if triggered by the User clicking on the Roles table
        related_tools = df_role_to_tool[df_role_to_tool["Role"] == selected_role]["Tool"].drop_duplicates().tolist()
        df_plot["Color"] = df_plot.apply(
            lambda row:
            tool_type_colors[row["Tool_Type"]] if row["Tool"] in related_tools
            else
            tool_type_colors_2[row["Tool_Type"]],
            axis=1
        )
    elif selected_tool is not None: # if triggered by the User clicking on the Word cloud
        df_plot["Color"] = df_plot.apply(
            lambda row:
            tool_type_colors[row["Tool_Type"]] if row["Tool"] == selected_tool
            else
            tool_type_colors_2[row["Tool_Type"]],
            axis=1
        )
    elif selected_task is not None: # if triggered by the User clicking on the Tasks table
        related_tools = df[df["Task"] == selected_task]["Tool"].drop_duplicates().tolist()
        df_plot["Color"] = df_plot.apply(
            lambda row:
            tool_type_colors[row["Tool_Type"]] if row["Tool"] in related_tools
            else
            tool_type_colors_2[row["Tool_Type"]],
            axis=1
        )
    elif selected_achievement is not None:  # if triggered by the User clicking on the Tasks table
        related_tools = df[df["Achievement"] == selected_achievement]["Tool"].drop_duplicates().tolist()
        df_plot["Color"] = df_plot.apply(
            lambda row:
            tool_type_colors[row["Tool_Type"]] if row["Tool"] in related_tools
            else
            tool_type_colors_2[row["Tool_Type"]],
            axis=1
    )

    fig = px.scatter(
        df_plot,
        x=df_plot["x_pos"],
        y=df_plot["y_pos"],
        text="Tool",
        width=700,
        height=300
    )
    fig.update_traces(
        mode="text",
        textposition="middle center",
        textfont_size=size_scaled,
        textfont_color=df_plot["Color"],
        hovertemplate="Tool: %{text}<br>Type: %{customdata[0]}<br>Size: %{customdata[1]}",
        customdata=df_plot[["Tool_Type", "Tool_Size"]]
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, fixedrange=True),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, fixedrange=True),
        plot_bgcolor='white',
        autosize=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    fig.update_yaxes(visible=False)
    fig.update_xaxes(visible=False)

    return fig


def create_gantt(selected_client_order=None, selected_role=None, selected_tool=None, selected_task=None, selected_achievement=None):
    df_plot = df_gantt.copy()

    # apply darker gray color to the highlighted Gantt bars (if any)
    if selected_client_order is not None: # if triggered by the User clicking on the Clients table
        df_plot.loc[df_plot['Client_Order'] == selected_client_order, 'color'] = 'dimgray'
    elif selected_role is not None: # if triggered by the User clicking on the Roles table
        related_client_orders = df[df["Role"] == selected_role]["Client_Order"].unique()
        df_plot.loc[df_plot['Client_Order'].isin(related_client_orders), 'color'] = 'dimgray'
    elif selected_tool is not None:
        related_client_orders = df[df["Tool"] == selected_tool]["Client_Order"].unique()
        df_plot.loc[df_plot['Client_Order'].isin(related_client_orders), 'color'] = 'dimgray'
    elif selected_task is not None:
        related_client_orders = df[df["Task"] == selected_task]["Client_Order"].unique()
        df_plot.loc[df_plot['Client_Order'].isin(related_client_orders), 'color'] = 'dimgray'
    elif selected_achievement is not None:
        related_client_orders = df[df["Achievement"] == selected_achievement]["Client_Order"].unique()
        df_plot.loc[df_plot['Client_Order'].isin(related_client_orders), 'color'] = 'dimgray'

    clients_list = list(dict.fromkeys(df_plot["Client_Name_Full"].tolist()[::-1]))

    selected_client_row = clients_orders_list.index(selected_client_order) if selected_client_order is not None else None

    fig = px.timeline(
        df_plot,
        x_start="Start_Date",
        x_end="End_Date",
        y="Client_Name_Full",
        color="color",
        color_discrete_map="identity",
        category_orders={"Client_Name_Full": clients_list}
    )

    shapes = [] # blue highlight on selection if any (from callbacks) + row banding (default)
    for i in range(len(clients_list)):
        if selected_client_order is not None and i == len(clients_list) - selected_client_row - 1:  # if triggered by the User clicking on the Clients table
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
        elif i % 2 == 0: # above is blue highlighting if any (from callbacks), which overrides the default row banding (below)
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


        if selected_role is not None or selected_tool is not None or selected_task is not None or selected_achievement is not None:
            # if triggered by the User clicking on the Roles/Tools/Tasks/Achievements table
            if all_clients_orders[i] in related_client_orders:
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
            elif i % 2 == 0: # above is blue highlighting if any (from callbacks), which overrides the default row banding (below)
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


#########################################################################################################################################################
###################################################################### APP LAYOUT #######################################################################
#########################################################################################################################################################


app = Dash(__name__)


app.title = 'Yury Ulasenka | CV'


app.layout = html.Div([
    html.Div(
        "Yury Ulasenka | Interactive Resume/CV",
        style={"position": "absolute", "left": "27px", "top": "10px", "backgroundColor": "white", "height": "30px",
               "padding": "5px", "fontSize": "20px", "fontWeight": "bold", "color": "rgb(0,0,0)", "zIndex": 1}
    ),
    html.Div(
        [
        "Click on views to filter/highlight each other. Click outside views to reset. Hover over views for tooltips.",
        ],
        style={"position": "absolute", "left": "27px", "top": "40px", "backgroundColor": "white", "height": "25px",
               "padding": "5px", "fontSize": "12px", "fontWeight": "bold", "color": "rgb(102,102,102)", "fontStyle": "italic", "zIndex": 1}
    ),
    html.Div(
        children=[
            html.Div(
                dcc.Graph(id="gantt-chart", figure=create_gantt(), config={"displayModeBar": False, "displaylogo": False}),
                style={"position": "absolute", "left": "0px", "top": "25px", "width": "300px", "height": "376px", "borderTop": "1px solid lightgray", "zIndex": 2}
            ),
            html.Div(
                "Timeline / Employer",
                style={"position": "absolute", "left": "0px", "top":  "0px","backgroundColor": "white", "height": "25px",
                       "padding": "5px", "fontSize": "11px", "fontWeight": "bold", "color": "rgb(85,85,85)", "zIndex": 1}
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
                    style_cell={"textAlign": "left", "border": "none", "fontWeight": "bold", "color": "rgb(51,51,51)"},
                    style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "rgb(85,85,85)", "backgroundColor": "white", "fontSize": "11px"},
                    style_data_conditional=clients_style,
                    css=[{"selector": ".show-hide", "rule": "display: none"}, {"selector": ".dash-spreadsheet tr", "rule": "height: 25px;"}],
                ),
                style={"position": "absolute", "left": "285px", "top": "0px", "width": "750px", "height": "375px", "zIndex": 3}
            ),
            html.Div(
                dash_table.DataTable(
                    id="roles-table",
                    data=df_roles.to_dict("records"),
                    columns=[{"name": "Role", "id": "Role"}],
                    style_cell={"textAlign": "left", "border": "none", "color": "rgb(85,85,85)"},
                    style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "rgb(85,85,85)", "backgroundColor": "white", "fontSize": "11px"},
                    style_data_conditional=roles_style,
                    css=[{"selector": ".dash-spreadsheet tr", "rule": "height: 29px;"}],
                ),
                style={"position": "absolute", "left": "1080px", "top": "0px", "width": "300px", "height": "325px", "zIndex": 2}
            ),
        ],
        style={"position": "relative", "left": "20px", "top": "80px"},
    ),

    html.Div(
        children=[
            html.Div(
                dash_table.DataTable(
                    id="achievements-table",
                    data=df_achievements.to_dict("records"),
                    columns=[{"name": "Achievement", "id": "Achievement"}],
                    style_cell={"textAlign": "left", "border": "none", "color": "rgb(51,51,51)", "fontWeight": "bold"},
                    style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "rgb(85,85,85)", "backgroundColor": "white", "fontSize": "11px"},
                    style_table={"overflowY": "auto", "height": "150px"},
                    style_data_conditional=clients_style,
                    fixed_rows={'headers': True},
                    css=[{"selector": ".dash-spreadsheet tr", "rule": "height: 25px;"}]
                ),
                style={"position": "absolute", "left": "0px", "top": "0px", "width": "650px", "height": "150px", "zIndex": 2}
            ),
            html.Div(
                dash_table.DataTable(
                    id="tasks-table",
                    data=df_tasks.to_dict("records"),
                    columns=[{"name": "Task", "id": "Task"}],
                    style_cell={"textAlign": "left", "border": "none", "color": "rgb(85,85,85)"},
                    style_header={"borderBottom": "1px solid lightgray", "fontWeight": "bold", "color": "rgb(85,85,85)", "backgroundColor": "white", "fontSize": "11px"},
                    style_table={"overflowY": "auto", "height": "150px"},
                    style_data_conditional=clients_style,
                    fixed_rows={'headers': True},
                    css=[{"selector": ".dash-spreadsheet tr", "rule": "height: 25px;"}]
                ),
                style={"position": "absolute", "left": "0px", "top": "175px", "width": "650px", "height": "150px", "zIndex": 2}
            ),
            html.Div(
                "Tool",
                style={"position": "absolute", "left": "680px", "top": "0px", "backgroundColor": "white", "height": "25px",
                       "padding": "5px", "fontSize": "11px", "fontWeight": "bold", "color": "rgb(85,85,85)", "zIndex": 1}
            ),
            html.Div(
                dcc.Graph(
                    id="word-cloud",
                    figure=create_wordcloud(),
                    config={"displayModeBar": False, "displaylogo": False},
                ),
                style={"position": "absolute", "left": "680px", "top": "25px", "borderTop": "1px solid lightgray", "zIndex": 2}
            )
        ],
        style={"position": "relative", "left": "20px", "top": "490px"},
    ),
    html.Div(
        id="background",
        style={"position": "absolute", "left": "0px", "top": "0px", "width": "95vw", "height": "95vh", "backgroundColor": "lavender", "zIndex": 0}
    ),


    html.Div(
        children=[
            html.Div(
                html.A(
                    html.Img(
                        src="https://raw.githubusercontent.com/half-man-half-potato/cv/master/assets/linkedin.png",
                        style={"width": "25px", "height": "auto"}
                    ),
                    style={"textAlign": "center", "position": "absolute", "left": "45px", "top": "0px", "zIndex": 1},
                    href="https://www.linkedin.com/in/yury-ulasenka/",
                    target="_blank"
                )
            ),
            html.Div(
                html.A(
                    html.Img(
                        src="https://raw.githubusercontent.com/half-man-half-potato/cv/master/assets/github.png",
                        style={"width": "25px", "height": "auto"}
                    ),
                    style={"textAlign": "center", "position": "absolute", "left": "80px", "top": "0px", "zIndex": 1},
                    href="https://github.com/half-man-half-potato/cv",
                    target="_blank"
                )
            )
        ],
        style={"position": "relative", "left": "1300px", "top": "10px"},
    )


])


#########################################################################################################################################################
####################################################################### CALLBACKS #######################################################################
#########################################################################################################################################################


#__________________________________________________
# 1. PROJECTS table: if the User clicks on the Projects table:
#__________________________________________________


global callback_counter
callback_counter = 0


# 1.a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("roles-table", "active_cell", allow_duplicate=True),
    Output("roles-table", "selected_cells", allow_duplicate=True),
    Output("achievements-table", "active_cell", allow_duplicate=True),
    Output("achievements-table", "selected_cells", allow_duplicate=True),
    Output("tasks-table", "active_cell", allow_duplicate=True),
    Output("tasks-table", "selected_cells", allow_duplicate=True),
    Input("projects-table", "active_cell"),
    prevent_initial_call=True
)
def projects_table_deactivate(active_cell):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: projects_table_deactivate: active_cell is {active_cell}')
        raise PreventUpdate ## 1-6

    print(f'{callback_counter}.: projects_table_deactivate: active_cell is NOT None')
    return None, [], None, [], None, []


# 1-b. update formatting in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True), # 1. Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True), # 2. Projects
    Output("roles-table", "style_data_conditional", allow_duplicate=True), # 3. Roles
    Output("achievements-table", "data", allow_duplicate=True), # 4. Achievements
    Output("tasks-table", "data", allow_duplicate=True), # 5. Tasks
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    Input("projects-table", "active_cell"),
    Input("projects-table", "data"),
    prevent_initial_call=True
)
def projects_table_update(active_cell, data):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: projects_table_update: active_cell is {active_cell}')
        raise PreventUpdate ## 1-6

    active_cell_row = active_cell["row"]
    selected_client_order = data[active_cell_row]["Client_Order"]

    clients_style_conditional = [{"if": {"row_index": active_cell_row}, "backgroundColor": "lightblue"}]

    related_roles = df[df["Client_Order"] == selected_client_order]["Role"].unique()
    roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{role}"'}, "backgroundColor": "lightblue"} for role in related_roles]

    filtered_achievements = df[df["Client_Order"] == selected_client_order]["Achievement"].drop_duplicates().dropna().sort_values()

    filtered_tasks = df[df["Client_Order"] == selected_client_order]["Task"].drop_duplicates().sort_values()

    print(f'{callback_counter}.: projects_table_update: active_cell is NOT None')

    return (
            create_gantt(selected_client_order=selected_client_order), # 1
            clients_style + clients_style_conditional, # 2
            roles_style + roles_style_conditional, # 3
            pd.DataFrame({"Achievement": filtered_achievements}).sort_index().to_dict("records"), # 4
            pd.DataFrame({"Task": filtered_tasks}).sort_index().to_dict("records"), # 5
            create_wordcloud(selected_client_order=selected_client_order) # 6
            )


#__________________________________________________
# 2. ROLES table: if the User clicks on the Roles table:
#__________________________________________________


# 2.a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("projects-table", "active_cell", allow_duplicate=True),
    Output("projects-table", "selected_cells", allow_duplicate=True),
    Output("achievements-table", "active_cell", allow_duplicate=True),
    Output("achievements-table", "selected_cells", allow_duplicate=True),
    Output("tasks-table", "active_cell", allow_duplicate=True),
    Output("tasks-table", "selected_cells", allow_duplicate=True),
    Input("roles-table", "active_cell"),
    prevent_initial_call=True
)
def roles_table_deactivate(active_cell):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: roles_table_deactivate: active_cell is {active_cell}')
        raise PreventUpdate ## 1-6

    print(f'{callback_counter}.: roles_table_deactivate: active_cell is NOT None')
    return None, [], None, [], None, []


# 2.b. update formatting in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True),  # 1. Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True),  # 2. Client
    Output("roles-table", "style_data_conditional", allow_duplicate=True), # 3. Roles
    Output("achievements-table", "data", allow_duplicate=True),  # 4. Achievements
    Output("tasks-table", "data", allow_duplicate=True),  # 5. Tasks
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    Input("roles-table", "active_cell"),
    Input("roles-table", "data"),
    prevent_initial_call=True
)
def roles_table_update(active_cell, data):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: roles_table_update: active_cell is {active_cell}')
        raise PreventUpdate ## 1-6

    active_cell_row = active_cell["row"]
    selected_role = data[active_cell_row]["Role"]

    related_client_orders = df[df["Role"] == selected_role]["Client_Order"].unique()
    clients_style_conditional = [{"if": {"filter_query": f'{{Client_Order}} = "{order}"'}, "backgroundColor": "lightblue"} for order in related_client_orders]

    roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{selected_role}"'}, "backgroundColor": "lightblue"}]

    filtered_achievements = df_role_to_achievement[df_role_to_achievement["Role"] == selected_role]["Achievement"].drop_duplicates().dropna().sort_values()

    filtered_tasks = df_role_to_task[df_role_to_task["Role"] == selected_role]["Task"].drop_duplicates().sort_values()

    print(f'{callback_counter}.: roles_table_update: active_cell is NOT None')

    return (
            create_gantt(selected_role=selected_role),  # 1
            clients_style + clients_style_conditional, # 2
            roles_style + roles_style_conditional, # 3
            pd.DataFrame({"Achievement": filtered_achievements}).sort_index().to_dict("records"),  # 4
            pd.DataFrame({"Task": filtered_tasks}).sort_index().to_dict("records"),  # 5
            create_wordcloud(selected_role=selected_role)  # 6
            )


#__________________________________________________
# 3. WORD CLOUD: if the User clicks on the Word Cloud:
#__________________________________________________


# 3.a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("projects-table", "active_cell", allow_duplicate=True),
    Output("projects-table", "selected_cells", allow_duplicate=True),
    Output("roles-table", "active_cell", allow_duplicate=True),
    Output("roles-table", "selected_cells", allow_duplicate=True),
    Output("achievements-table", "active_cell", allow_duplicate=True),
    Output("achievements-table", "selected_cells", allow_duplicate=True),
    Output("tasks-table", "active_cell", allow_duplicate=True),
    Output("tasks-table", "selected_cells", allow_duplicate=True),
    Input("word-cloud", "clickData"),
    prevent_initial_call=True
)
def word_cloud_deactivate(clickData):
    global callback_counter
    callback_counter += 1

    if clickData is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: word_cloud_deactivate: clickData is {clickData}')
        raise PreventUpdate

    print(f'{callback_counter}.: word_cloud_deactivate: clickData is NOT None')
    return None, [], None, [], None, [], None, []


# 3.b. update formatting in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True),  # 1 Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True), # 2 Clients
    Output("roles-table", "style_data_conditional", allow_duplicate=True),  # 3 Roles
    Output("achievements-table", "data", allow_duplicate=True),  # 4. Achievements
    Output("tasks-table", "data", allow_duplicate=True),  # 5. Tasks
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    Input("word-cloud", "clickData"),
    prevent_initial_call=True
)
def word_cloud_update(clickData):
    global callback_counter
    callback_counter += 1

    if clickData is None:
        print(f'{callback_counter}.: word_cloud_update: clickData is {clickData}')
        raise PreventUpdate ##1-6

    print(f'{callback_counter}.: word_cloud_update: clickData is NOT None')

    selected_tool = clickData["points"][0]["text"]
    related_client_orders = df[df["Tool"] == selected_tool]["Client_Order"].drop_duplicates().tolist()

    clients_style_conditional = [{"if": {"filter_query": f'{{Client_Order}} = "{order}"'}, "backgroundColor": "lightblue"} for order in related_client_orders]

    related_roles = df_role_to_tool[df_role_to_tool["Tool"] == selected_tool]["Role"].unique()
    roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{role}"'}, "backgroundColor": "lightblue"} for role in related_roles]

    filtered_achievements = df[df["Tool"] == selected_tool]["Achievement"].drop_duplicates().dropna().sort_values() # ToDo: create new relations

    filtered_tasks = df[df["Tool"] == selected_tool]["Task"].drop_duplicates().sort_values() # ToDo: create new relations

    return (
            create_gantt(selected_tool=selected_tool),  # 1
            clients_style + clients_style_conditional, # 2
            roles_style + roles_style_conditional,  # 3
            pd.DataFrame({"Achievement": filtered_achievements}).sort_index().to_dict("records"),  # 4
            pd.DataFrame({"Task": filtered_tasks}).sort_index().to_dict("records"),  # 5
            create_wordcloud(selected_tool=selected_tool)  # 6
            )


#__________________________________________________
# 4. TASKS: if the User clicks on the Task table:
#__________________________________________________


# 4.a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("projects-table", "active_cell", allow_duplicate=True),
    Output("projects-table", "selected_cells", allow_duplicate=True),
    Output("roles-table", "active_cell", allow_duplicate=True),
    Output("roles-table", "selected_cells", allow_duplicate=True),
    Output("achievements-table", "active_cell", allow_duplicate=True),
    Output("achievements-table", "selected_cells", allow_duplicate=True),
    Input("tasks-table", "active_cell"),
    prevent_initial_call=True
)
def tasks_deactivate(active_cell):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: tasks_deactivate: active_cell is {active_cell}')
        raise PreventUpdate

    print(f'{callback_counter}.: tasks_deactivate: active_cell is NOT None')
    return None, [], None, [], None, []


# 4.b. update formatting in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True), # 1. Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True), # 2. Projects
    Output("roles-table", "style_data_conditional", allow_duplicate=True), # 3. Roles
    Output("achievements-table", "data", allow_duplicate=True), # 4. Achievements
    Output("tasks-table", "style_data_conditional", allow_duplicate=True), # 5. Tasks
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    Input("tasks-table", "active_cell"),
    Input("tasks-table", "data"),
    prevent_initial_call=True
)
def tasks_update(active_cell, data):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: tasks_update: active_cell is {active_cell}')
        raise PreventUpdate ## 1-6

    active_cell_row = active_cell["row"]
    selected_task = data[active_cell_row]["Task"]

    related_client_orders = df[df["Task"] == selected_task]["Client_Order"].unique()
    clients_style_conditional = [{"if": {"filter_query": f'{{Client_Order}} = "{order}"'}, "backgroundColor": "lightblue"} for order in related_client_orders]

    related_roles = df[df["Task"] == selected_task]["Role"].unique()
    roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{role}"'}, "backgroundColor": "lightblue"} for role in related_roles]

    tasks_style_conditional = [{"if": {"row_index": active_cell_row}, "backgroundColor": "lightblue"}]

    filtered_achievements = df[df["Task"] == selected_task]["Achievement"].drop_duplicates().dropna().sort_values() # ToDo: add new relations

    print(f'{callback_counter}.: tasks_update: active_cell is NOT None')

    return (
            create_gantt(selected_task=selected_task), # 1
            clients_style + clients_style_conditional, # 2
            roles_style + roles_style_conditional, # 3
            pd.DataFrame({"Achievement": filtered_achievements}).sort_index().to_dict("records"), # 4
            clients_style + tasks_style_conditional, # 5
            create_wordcloud(selected_task=selected_task) # 6
            )


#__________________________________________________
# 5. ACHIEVEMENTS: if the User clicks on the Achievements table:
#__________________________________________________


# 5.a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("projects-table", "active_cell", allow_duplicate=True),
    Output("projects-table", "selected_cells", allow_duplicate=True),
    Output("roles-table", "active_cell", allow_duplicate=True),
    Output("roles-table", "selected_cells", allow_duplicate=True),
    Output("tasks-table", "active_cell", allow_duplicate=True),
    Output("tasks-table", "selected_cells", allow_duplicate=True),
    Input("achievements-table", "active_cell"),
    prevent_initial_call=True
)
def achievements_deactivate(active_cell):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: achievements_deactivate: active_cell is {active_cell}')
        raise PreventUpdate

    print(f'{callback_counter}.: achievements_deactivate: active_cell is NOT None')
    return None, [], None, [], None, []


# 5.b. update formatting in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True), # 1. Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True), # 2. Projects
    Output("roles-table", "style_data_conditional", allow_duplicate=True), # 3. Roles
    Output("achievements-table", "style_data_conditional", allow_duplicate=True), # 4. ACHIEVEMENTS style
    Output("tasks-table", "data", allow_duplicate=True), # 5. Tasks
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    # Output("achievements-table", "data", allow_duplicate=True), # 7. ACHIEVEMENTS (full) data
    # Output("achievements-table", "active_cell", allow_duplicate=True),  # 8. ACHIEVEMENTS (new) active_cell
    # Output("achievements-table", "selected_cells", allow_duplicate=True),  # 9. ACHIEVEMENTS (new) selected_cells (same as active_cell)
    Input("achievements-table", "active_cell"),
    Input("achievements-table", "data"),
    prevent_initial_call=True
)
def achievements_update(active_cell, data):
    global callback_counter
    callback_counter += 1

    if active_cell is None: # if triggered by a chained callback instead, do not update the callback output(s) and exit the function
        print(f'{callback_counter}.: achievements_update: active_cell is {active_cell}')
        raise PreventUpdate

    active_cell_row = active_cell["row"]
    selected_achievement = data[active_cell_row]["Achievement"]

    # active_cell_index = df_achievements.index[df_achievements["Achievement"] == selected_achievement].tolist()[0]
    # active_cell_row_new = df_achievements.index.get_loc(active_cell_index)
    # new_active_cell = {"row": active_cell_row_new, "column": 0, "column_id": "Achievement"}

    related_client_orders = df[df["Achievement"] == selected_achievement]["Client_Order"].unique()
    clients_style_conditional = [{"if": {"filter_query": f'{{Client_Order}} = "{order}"'}, "backgroundColor": "lightblue"} for order in related_client_orders]

    related_roles = df[df["Achievement"] == selected_achievement]["Role"].unique()
    roles_style_conditional = [{"if": {"filter_query": f'{{Role}} = "{role}"'}, "backgroundColor": "lightblue"} for role in related_roles]

    achievements_style_conditional = [{"if": {"row_index": active_cell_row}, "backgroundColor": "lightblue"}]

    filtered_tasks = df[df["Achievement"] == selected_achievement]["Task"].drop_duplicates().sort_values() # ToDo: add new relations

    print(f'{callback_counter}.: achievements_update: active_cell is NOT None')

    return (
            create_gantt(selected_achievement=selected_achievement), # 1
            clients_style + clients_style_conditional, # 2
            roles_style + roles_style_conditional, # 3
            clients_style + achievements_style_conditional, # 4
            pd.DataFrame({"Task": filtered_tasks}).sort_index().to_dict("records"), # 5
            create_wordcloud(selected_achievement=selected_achievement), # 6
            # df_achievements.to_dict("records"), # 7
            # new_active_cell, # 8
            # new_active_cell # 9
            )


#__________________________________________________
# BACKGROUND: if the User clicks on the background:
#__________________________________________________


# a. deactivate/unselect active/selected cells in other elements
@app.callback(
    Output("projects-table", "active_cell", allow_duplicate=True),
    Output("projects-table", "selected_cells", allow_duplicate=True),
    Output("roles-table", "active_cell", allow_duplicate=True),
    Output("roles-table", "selected_cells", allow_duplicate=True),
    Output("achievements-table", "active_cell", allow_duplicate=True),
    Output("achievements-table", "selected_cells", allow_duplicate=True),
    Output("tasks-table", "active_cell", allow_duplicate=True),
    Output("tasks-table", "selected_cells", allow_duplicate=True),
    Input("background", "n_clicks"),
    prevent_initial_call=True
)
def background_deactivate(n_clicks):
    global callback_counter
    callback_counter += 1

    print(f'{callback_counter}.: clear_active_cell_deactivate')
    return None, [], None, [], None, [], None, []


# b. set formatting to default in other elements
@app.callback(
    Output("gantt-chart", "figure", allow_duplicate=True),  # 1. Gantt
    Output("projects-table", "style_data_conditional", allow_duplicate=True),  # 2. Client
    Output("roles-table", "style_data_conditional", allow_duplicate=True), # 3. Roles
    Output("achievements-table", "data", allow_duplicate=True),  # 4.1 Achievements: data (remove filters) Comment: NEW!
    Output("achievements-table", "style_data_conditional", allow_duplicate=True),  # 4.2 Achievements: formatting (remove highlighting)  Comment: NEW!
    Output("tasks-table", "data", allow_duplicate=True),  # 5.1 Tasks: data (remove filters) Comment: NEW!
    Output("tasks-table", "style_data_conditional", allow_duplicate=True),  # 5.2 Tasks: formatting (remove highlighting)  Comment: NEW!
    Output("word-cloud", "figure", allow_duplicate=True),  # 6. Word cloud
    Input("background", "n_clicks"),
    prevent_initial_call=True
)
def background_update(n_clicks):
    global callback_counter
    callback_counter += 1

    print(f'{callback_counter}.: clear_active_cell_update')
    return (
            create_gantt(), # 1
            clients_style, # 2
            roles_style, # 3
            df_achievements.to_dict("records"), # 4.1  Comment: NEW
            clients_style,  # 4.2 Comment: NEW
            df_tasks.to_dict("records"), # 5.1  Comment: NEW!
            clients_style,  # 5.2 Comment: NEW
            create_wordcloud() # 6
            )
