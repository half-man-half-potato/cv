import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load CSV directly from the raw GitHub link
url = "https://raw.githubusercontent.com/half-man-half-potato/sp_celebrities/main/sp_uncensored_only.csv"
df = pd.read_csv(url)

# Drop rows where person_name is NaN
df = df.dropna(subset=["person_name"])

# Create the Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Top 10 South Park Guests by Episode Count", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Season(s):"),
        dcc.Dropdown(
            id="season-filter",
            options=[{"label": str(season), "value": season} for season in sorted(df["season_number"].dropna().unique())],
            multi=True,
            placeholder="Select one or more seasons"
        )
    ], style={"width": "250px", "margin-bottom": "20px"}),

    dcc.Graph(id="bar-chart")
])

# Callback to update chart based on season filter
@app.callback(
    Output("bar-chart", "figure"),
    Input("season-filter", "value")
)
def update_chart(selected_seasons):
    # Filter by season if selected
    filtered_df = df
    if selected_seasons:
        filtered_df = filtered_df[filtered_df["season_number"].isin(selected_seasons)]

    # Group by person_name, count unique episodes
    top_df = (
        filtered_df.groupby("person_name")["episode_name"]
        .nunique()
        .reset_index()
        .rename(columns={"episode_name": "episode_count"})
    )

    # Sort and take top 10
    top_df = top_df.sort_values(by="episode_count", ascending=False).head(10)

    # Horizontal bar chart
    fig = px.bar(
        top_df,
        x="episode_count",
        y="person_name",
        orientation="h",
        text="episode_count",
        title="Top 10 Guests by Episode Count"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},  # so largest bar is at top
        xaxis_title="Episode Count",
        yaxis_title="Person Name",
        plot_bgcolor="white"
    )

    return fig