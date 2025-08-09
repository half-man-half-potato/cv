import pandas as pd
from dash import Dash, dash_table, html

# Load CSV from raw GitHub URL
url = "https://github.com/half-man-half-potato/cv/raw/master/data.csv"
df = pd.read_csv(url)

# Select columns, drop duplicates, sort by Client_ID ascending
cols = ['Client_ID', 'Employer', 'Country', 'Client_Name_Full', 'Project']
df_clean = df[cols].drop_duplicates().sort_values('Client_ID').reset_index(drop=True)

# We'll keep Client_ID in data for sorting, but exclude from displayed columns
display_cols = ['Employer', 'Country', 'Client_Name_Full', 'Project']

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Client Data Table (Client_ID hidden)"),
    dash_table.DataTable(
        id='client-table',
        columns=[{"name": col, "id": col} for col in display_cols],
        data=df_clean.to_dict('records'),
        page_action='none',  # show all rows
        style_table={
            'overflowX': 'visible',
            'overflowY': 'visible',
            'maxHeight': 'none',
        },
        style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
            'minWidth': '120px',
            'width': '120px',
            'maxWidth': '180px',
        },
    )
])
