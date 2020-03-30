import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np


df_github = pd.DataFrame()
country_dropdown_list = []
dates = []
region_dictionary = defaultdict(list)


def pull_data():
    global df_github
    df_github = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'
                            'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    update_country_list()


def update_country_list():
    global country_dropdown_list
    global last_update
    country_list = []
    global region_dictionary
    region_dictionary = defaultdict(list)
    df_find_options = df_github.copy(deep=True) \
        .drop(columns=df_github.loc[:, ~df_github.columns.isin(['Province/State', 'Country/Region'])])

    for row in df_find_options.itertuples(index=False):
        region = row[0]
        country = row[1]
        if region == 'Recovered':
            continue
        try:
            if np.isnan(region) and country not in country_list:
                country_list.append(country)
        except TypeError:
            if country not in country_list:
                country_list.append(country)
            region_dictionary[country].append(region)

    for country in country_list:
        country_dropdown_list.append({'label': country, 'value': country})
    find_dates()


def find_dates():
    global df_github
    for col in df_github.columns:
        try:
            dates.append(datetime.strptime(col, '%m/%d/%y').date())
        except ValueError:
            continue
    return dates[-1]


pull_data()
last_update = find_dates()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1(children='COVID-19'),
    html.H4(children=f'Last updated: {last_update}',
            id='last_updated'),
    dcc.Interval(
            id='interval-component',
            interval=10*1000,  # in milliseconds
            n_intervals=0
            ),
    html.Label('Country'),
    dcc.Dropdown(
            id='dropdown_country',
            options=country_dropdown_list,
            value='US',
        ),
    html.Label('Region'),
    dcc.Dropdown(
        id='dropdown_region',
        options=[],
        value=[],
        disabled=True,
    ),
    dcc.Graph(id='cases_by_date'),
])


@app.callback(Output('last_updated', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_data(value):
    pull_data()
    return 'Last updated: ' + str(find_dates())


@app.callback([Output('dropdown_region', 'options'),
               Output('dropdown_region', 'disabled'),
               Output('dropdown_region', 'value')],
              [Input('dropdown_country', 'value')])
def update_region(value):
    options = []
    if value not in region_dictionary.keys():
        return options, True, None
    else:
        for v in region_dictionary[value]:
            options.append({'label': v, 'value': v})
        return options, False, None


@app.callback(Output('cases_by_date', 'figure'),
              [Input('dropdown_country', 'value'),
               Input('dropdown_region', 'value')])
def update_cases_by_date_chart(country, region):
    print('updating graph', country, region)
    if not region:
        # for countries with regions defined, will need to squash all cases into one
        df = df_github.copy(deep=True)
        df = df[df['Country/Region'] == country]
        df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'], inplace=True)
        df = df.transpose()
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'confirmed_cases'}, inplace=True)

        fig = px.line(df, x='date', y='confirmed_cases', title=country)
        return fig
    else:
        df = df_github.copy(deep=True)
        df = df[df['Province/State'] == region]
        df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'], inplace=True)
        df = df.transpose()
        df.reset_index(inplace=True)
        df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'confirmed_cases'}, inplace=True)

        fig = px.line(df, x='date', y='confirmed_cases', title=region)
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
