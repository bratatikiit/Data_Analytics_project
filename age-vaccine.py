
#!pip install pandas as pd 
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Read data from your CSV file (replace 'your_vaccination_data.csv' with the actual path)
df = pd.read_csv('./vaccinations-by-age-group.csv')
# Data cleaning and transformation (if needed)
# Assuming dates are in 'DD/MM/YYYY' format, convert to datetime
if 'date' in df.columns:  # Check if 'date' column exists
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    # Extract year
    df['year'] = df['date'].dt.year

# Define visualization function (using Plotly Express)
def create_visualization(selected_year, selected_country):
    filtered_df = df[df['year'] == selected_year]
    if selected_country:
        filtered_df = filtered_df[df['location'] == selected_country]

    fig = px.bar(
        filtered_df,
        x="age_group",
        y=["people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred", "people_with_booster_per_hundred"],
        barmode="group",  # Stack bars to show cumulative values
        title=f"Vaccination Rates in {selected_country or 'All Countries'} ({selected_year})"
    )
    fig.update_layout(legend_title_text="Vaccination Status")
    fig.update_traces(marker_line_color='black', marker_line_width=1)  # Improve bar visibility

    # Convert plot to PNG for Dash usage
    img_bytes = BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    encoded_img = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    return f'data:image/png;base64,{encoded_img}'

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Vaccination Rates by Country and Age Group"),
    html.Div([
        dcc.Dropdown(
            id="year-dropdown",
            options=[{'label': str(y), 'value': y} for y in df['year'].unique()],
             value=df['year'].max()  # Pre-select the latest year
        ),
        dcc.Dropdown(
            id="country-dropdown",
            options=[{'label': c, 'value': c} for c in df['location'].unique()] + [{'label': 'All Countries', 'value': None}],
            value=None  # Allow filtering by all countries
        )
    ]),
    html.Div(id='graph-container'),
])

# Callback to update the graph
@app.callback(
    Output(component_id='graph-container', component_property='children'),
    [Input(component_id='year-dropdown', component_property='value'),
     Input(component_id='country-dropdown', component_property='value')]
)
def update_graph(selected_year, selected_country):
    graph_image = create_visualization(selected_year, selected_country)
    return html.Img(src=graph_image)

if __name__ == '__main__':
    app.run_server(debug=True)