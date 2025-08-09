import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, html, dcc

# Load data
url = "https://raw.githubusercontent.com/half-man-half-potato/cv/master/data.csv"
df = pd.read_csv(url)

# Prepare df1
df1 = df[['Client_ID', 'Employer', 'Country', 'Client_Name_Full', 'Project']].drop_duplicates()
df1 = df1.sort_values('Client_ID').reset_index(drop=True)
df1 = df1.drop(columns=['Client_ID'])

# Prepare df2
df2 = df[['Client_ID', 'Start_Date', 'End_Date', 'Duration', 'Employer']].drop_duplicates()
df2 = df2.sort_values('Client_ID').reset_index(drop=True)

# Convert dates to datetime
df2['Start_Date'] = pd.to_datetime(df2['Start_Date'])
df2['End_Date'] = pd.to_datetime(df2['End_Date'])

# Create Gantt chart with Client_ID sorted descending on y-axis
fig = px.timeline(
    df2,
    x_start="Start_Date",
    x_end="End_Date",
    y="Client_ID",
    color="Employer",
    category_orders={"Client_ID": sorted(df2['Client_ID'].unique(), reverse=True)},
)

# Remove title, legend, and y axis labels
fig.update_layout(
    title_text='',
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
    height=600,
    yaxis=dict(showticklabels=False, visible=False),
    xaxis=dict(showgrid=True),
)

# Reverse y-axis to have descending order top to bottom
fig.update_yaxes(autorange="reversed")

# Dash app layout
app = Dash(__name__)

app.layout = html.Div(
    style={'display': 'flex', 'height': '650px', 'overflow': 'hidden', 'fontFamily': 'Arial, sans-serif'},
    children=[
        # Left: Gantt chart
        html.Div(
            dcc.Graph(figure=fig, config={'displayModeBar': False}),
            style={'flex': '0 0 50%', 'padding': '10px', 'boxSizing': 'border-box', 'height': '100%'}
        ),
        # Right: Data Table
        html.Div(
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df1.columns],
                data=df1.to_dict('records'),
                page_action='none',
                style_table={'height': '100%', 'overflowY': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'fontSize': '14px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '120px',
                },
                fixed_rows={'headers': True},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
            ),
            style={'flex': '0 0 50%', 'padding': '10px', 'boxSizing': 'border-box', 'height': '100%', 'overflow': 'hidden'}
        ),
    ]
)
