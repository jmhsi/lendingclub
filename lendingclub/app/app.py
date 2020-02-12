import os
import pandas as pd
from sqlalchemy import create_engine
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output


from lendingclub import config

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# load api_loans df and historical scores df
disk_engine = create_engine(f'sqlite:///{config.lc_api_db}')
df = pd.read_sql('lc_api_loans',
                 con=disk_engine,
                 parse_dates=[
                     'accept_d', 'exp_d', 'list_d', 'credit_pull_d',
                     'review_status_d', 'ils_exp_d', 'last_seen_list_d'
                 ])
hist_df = pd.read_feather(
    os.path.join(config.data_dir, 'all_eval_loan_info_scored.fth'))

# setup some constants for use in app
rounds = sorted(df['list_d'].dt.hour.unique())
min_date = df['list_d'].min().date()
max_date = df['list_d'].max().date()
print(min_date, max_date)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H3('API loans'),
    html.Div([
        dcc.DatePickerRange(id='api-loans-date-picker-range',
                            start_date=max_date,
                            end_date=max_date,
                            min_date_allowed=min_date,
                            # for some reason I couldn't select max date
                            max_date_allowed=max_date + pd.DateOffset(days=1),),
        html.Div(id='api-loans-date-picker-range-info')
    ]),
    html.Div([
        dcc.Dropdown(id='api-loans-round-dropdown',
                 options=[{'label':i, 'value': i} for i in rounds],
                 multi=True,
                 value=rounds),
        html.Div(id='api-loans-round-dropdown-info')
    ]),    
    dcc.Graph(id='api-loans-graph', ),
    dash_table.DataTable(
        id='api-table',
        columns=[{
            "name": i,
            "id": i
        } for i in df.columns],
        fixed_columns={
            'headers': True,
            'data': 1
        },
        fixed_rows={
            'headers': True,
            'data': 0
        },
        style_table={
            'maxHeight': '250px',
            'maxWidth': '900px',
            'overflowY': 'scroll',
            'overflowX': 'scroll'
        },
        style_cell={'width': '150px'},
        style_data_conditional=[{
            'if': {
                'row_index': 'odd'
            },
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': '1px solid pink',
        },
        style_data={},
    ),
    html.H3('CSV loans'),

])

##### CALLBACKS #####
@app.callback(
    Output('api-table', 'data'), 
    [Input('api-loans-date-picker-range', 'start_date'),
     Input('api-loans-date-picker-range', 'end_date'),
     Input('api-loans-round-dropdown', 'value'),]
)
def update_api_table(start_date, end_date, listing_sess):
    sub_df = df.query('list_d >= @start_date and list_d <= @end_date and list_d_hour in @listing_sess')
    return sub_df.to_dict('records')

@app.callback(
    Output('api-loans-date-picker-range-info', 'children'),
    [Input('api-loans-date-picker-range', 'start_date'),
     Input('api-loans-date-picker-range', 'end_date'),]
)
def update_api_loans_date_picker_range_info(start_date, end_date):
    return f'Dates selected from {start_date} to {end_date}'

@app.callback(
    Output('api-loans-round-dropdown-info', 'children'),
    [Input('api-loans-round-dropdown', 'value'),]
)
def update_api_loans_round_dropdown_info(value):
    '''
    So far, haven't been able to find how to sort multi-select dropdown.
    '''
    return f'Selected daily loan release rounds {", ".join([str(i) for i in sorted(value)])}'

@app.callback(
    Output('api-loans-graph', 'figure'), 
    [Input('api-loans-date-picker-range', 'start_date'),
     Input('api-loans-date-picker-range', 'end_date'),
     Input('api-loans-round-dropdown', 'value'),]
)
def update_api_loans_graph(start_date, end_date, listing_sess):
    sub_df = df.query('list_d >= @start_date and list_d <= @end_date and list_d_hour in @listing_sess')
    fig = px.histogram(sub_df, x='catboost_comb_20', nbins=100, histnorm='probability density', color='sub_grade', marginal='rug')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
