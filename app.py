import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import datetime
from collections import defaultdict
import pandas as pd
import numpy as np

df_raw_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'
                          'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
dates = []
country_lst = []
sub_country_dict = defaultdict(list)


# def create_df(df):
#     df = df[df['Country/Region'] == 'US']
#     df.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'], inplace=True)
#     df = df.transpose()
#     df.reset_index(inplace=True)
#     df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'confirmed_cases'}, inplace=True)


def find_dates():
    df_dates = df_raw_data
    for col in df_dates.columns:
        try:
            dates.append(datetime.strptime(col, '%m/%d/%y').date())
        except ValueError:
            # print(col)
            continue
    return dates[-1]


def country_list(df_read):
    sub_country_dict = defaultdict(list)
    df_options = df_read.copy(deep=True)\
        .drop(columns=df_read.loc[:, ~df_read.columns.isin(['Province/State', 'Country/Region'])])
    print(df_options)
    for row in df_options.itertuples(index=False):
        sub_country = row[0]
        country = row[1]
        try:
            if np.isnan(sub_country):
                country_lst.append(country)
        except TypeError:
            if country not in country_lst:
                country_lst.append(country)
            sub_country_dict[country].append(sub_country)


def update_country_list():
    country_dropdown_list_ = []
    raw_data = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'
                           'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    country_list(raw_data)
    for country in country_lst:
        country_dropdown_list_.append({'label': country, 'value': country})
    return country_dropdown_list_


last_update = find_dates()

country_list(df_raw_data)
country_dropdown_list = update_country_list()
# df = df_raw_data.copy(deep=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='COVID-19 by Country and Region'),
    html.H4(children=f'Last updated: {last_update}',
            id='last_updated'),
    dcc.Interval(
            id='interval-component',
            interval=10*1000,  # in milliseconds
            n_intervals=0
            ),
    html.H4(children='Select by country and region'),
    html.Label('Country'),
    dcc.Dropdown(
            id='dropdown_country',
            options=country_dropdown_list,
        ),
    html.Label('Region'),
    dcc.Dropdown(
        id='dropdown_region',
        options=[
            # {'label': 'Idaho', 'value': 'Idaho'},
            # {'label': 'Washington', 'value': 'Washington'},
            # {'label': 'New York', 'value': 'New York'}
        ],
        value=['Select'],
        disabled=True,
    ),

])


@app.callback(Output('last_updated', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_data(interval):
    update_country_list()
    return 'Last updated: ' + str(find_dates())


@app.callback([Output('dropdown_region', 'options'),
               Output('dropdown_region', 'disabled')],
              [Input('dropdown_country', 'value')])
def update_region(value):
    options = []
    if value not in sub_country_dict.keys():
        return options, True
    else:
        for v in sub_country_dict[value]:
            options.append({'label': v, 'value': v})
        return options, False


if __name__ == '__main__':
    app.run_server(debug=True)
