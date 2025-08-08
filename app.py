from dash import Dash,  html

app = Dash(__name__)

app.layout = html.Div(children=[
html.H2("the answer is..."),
html.H1("42")
])