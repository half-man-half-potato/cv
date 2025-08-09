import pandas as pd
import dash
from dash import dash_table, html

# 1. Load the CSV from the GitHub raw link
csv_url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(csv_url)

# 2. Keep only unique projects
projects_df = df[['Project']].drop_duplicates().reset_index(drop=True)

# 3. Build the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("List of Projects"),
    dash_table.DataTable(
        id="projects-table",
        columns=[{"name": "Project", "id": "Project"}],
        data=projects_df.to_dict("records"),
        style_table={"overflowX": "auto"},  # No vertical scrollbar
        style_cell={
            "textAlign": "left",
            "padding": "5px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "lightgrey",
            "fontWeight": "bold"
        },
        page_size=len(projects_df)  # Show all rows at once
    )
])