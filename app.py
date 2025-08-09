import pandas as pd
import dash
from dash import dash_table, html

# 1. Load CSV from GitHub raw link
csv_url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(csv_url)

# 2. Create DataFrame with Client ID list
clients_df = pd.DataFrame(df["Client ID"])

# 3. Build Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("List of Client IDs"),
    dash_table.DataTable(
        id="clients-table",
        columns=[{"name": "Client ID", "id": "Client ID"}],
        data=clients_df.to_dict("records"),
        style_table={"overflowX": "auto"},  # Only horizontal scroll if needed
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
        page_size=len(clients_df)  # Show all rows at once (no vertical scroll)
    )
])
