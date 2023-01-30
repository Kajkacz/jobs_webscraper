import pandas as pd
import dash
from dash import dcc,html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly
import plotly.graph_objects as go

import pymongo
import configparser
import os
import sys

import pdmongo as pdm
import pandas as pd
import json 

# Get config definition
config = configparser.ConfigParser()
config.read('config.ini')

suffix = "?retryWrites=true&w=majority"
# Get config definition
if os.path.exists('config.ini'):
    config = configparser.ConfigParser()
    config.read('config.ini')
    if len(sys.argv) > 1:
        local_db = sys.argv[1]
    else:
        local_db = config['mongodb']['local_db'] == 'True'
    # Connect to mongodb client
    if local_db:
        username = config['mongodb']['local_username']
        password = config['mongodb']['local_password']
        url = config['mongodb']['local_url']
        prefix = "mongodb"
        suffix = "?authSource=admin&readPreference=primary&ssl=false&directConnection=true"
    else:
        username = config['mongodb']['username']
        password = config['mongodb']['password']
        url = config['mongodb']['url']
        prefix = "mongodb+srv"
    db_name = config['mongodb']['db_name']
    coll_name = config['mongodb']['collection_name']
    rates_key = config['rates']['api_key']
mongo_url=f"{prefix}://{username}:{password}@{url}/{db_name}{suffix}"
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[db_name]
offers_collection = mydb[coll_name]
city_size_threshold = 20

cities_pipeline = [
    {'$unwind':'$salary'},
    {'$match':{"salary.average_pln":{"$ne" : "undisclosed"}}},
    {'$match':{"salary.currency":"PLN"}},
    {'$project':{
        'date':1,
        'city':1,
        'salary.average_pln':1,
        }
    },
    {'$group':
        {
        '_id': { 'city' : "$city" },
        'salary_average': { '$avg' : "$salary.average_pln" },
        'city_count': { '$count' : {} }
        }
    },
    {'$match':{"city_count":{"$gt":city_size_threshold}}},
    {'$sort':{"salary_average":1}},
]
city_salary_offers = offers_collection.aggregate(cities_pipeline)
city_salary_offers_df = pd.json_normalize(list(city_salary_offers))

fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=("Salary by City", "Salary by Tech", "Salary by Tech Level"), 
    specs=[
        [
            {"type": "bar"},{"type": "bar"}
        ],[ {"type": "scene","colspan": 2},None]
    ])

  

fig.add_trace(
    go.Bar(x=city_salary_offers_df['_id.city'], y=city_salary_offers_df['salary_average'],name="Salary by City",marker=dict(color=city_salary_offers_df['salary_average'],coloraxis="coloraxis")),
    row=1,col=1
)

tech_size_threshold = 50

tech_pipeline = [
    {'$unwind':'$salary'},
    {'$match':{"salary.average_pln":{"$ne" : "undisclosed"}}},
    {'$match':{"salary.currency":"PLN"}},
    {'$unwind':'$skills'},
    {'$project':{
        'skills.skill_name':1,
        'salary.average_pln':1,
        }
    },
    {'$group':
        {
        '_id': { 'tech' : "$skills.skill_name" },
        'salary_average': { '$avg' : "$salary.average_pln" },
        'tech_count': { '$count' : {} }
        }
    },
    {'$match':{"tech_count":{"$gt":tech_size_threshold}}},
    {'$sort':{"salary_average":1}},
]

tech_size_threshold_w_level = 100

tech_pipeline_w_level = [
    {'$unwind':'$salary'},
    {'$match':{"salary.average_pln":{"$ne" : "undisclosed"}}},
    {'$match':{"salary.currency":"PLN"}},
    {'$unwind':'$skills'},
    {'$project':{
        'skills.skill_name':1,
        'skills.skill_level':1,
        'salary.average_pln':1,
        }
    },
    {'$group':
        {
        '_id': { 'tech' : "$skills.skill_name",'level' : "$skills.skill_level" },
        'salary_average': { '$avg' : "$salary.average_pln" },
        'tech_count': { '$count' : {} }
        }
    },
    {'$match':{"tech_count":{"$gt":tech_size_threshold_w_level}}},
    {'$sort':{"salary_average":1}},
]

tech_salary_offers = offers_collection.aggregate(tech_pipeline)
tech_salary_offers_df = pd.json_normalize(list(tech_salary_offers))

fig.add_trace(
    go.Bar(
        x=tech_salary_offers_df['_id.tech'], 
        y=tech_salary_offers_df['salary_average'], 
        name="Salary by Tech",
        marker=dict(
            color=tech_salary_offers_df['salary_average'],
            coloraxis="coloraxis"
            )
        ),
    row=1,col=2
)

tech_salary_offers_w_level = offers_collection.aggregate(tech_pipeline_w_level)
tech_salary_offers_w_level_df = pd.json_normalize(list(tech_salary_offers_w_level))
#  grab x/y labels, create storage for z data
techs = tech_salary_offers_w_level_df['_id.tech'].unique()
levels = tech_salary_offers_w_level_df['_id.level'].unique()
levels.sort()
levels = [
    # "nice to have",
    "junior",
    "regular",
    "advanced",
    "master"
    ] #TODO Fix This
z_data = []

# extract z data using x,y coordinates within the dataframe
for tech in techs:
  row = []
  for level in levels:
    try:
        val = tech_salary_offers_w_level_df[
        (tech_salary_offers_w_level_df['_id.tech'] == tech) &
        (tech_salary_offers_w_level_df['_id.level'] == level)]['salary_average'].values[0]
    except IndexError:
        val = 0
    row.append(int(val))
  z_data.append(row)

for row in z_data:
    for i,value in enumerate(row):
        if value == 0:
            if i == 0:
                row[i] = min([v for v in row if v != 0])*0.9 if [v for v in row if v != 0] else 0
            else:
                row[i] = row[i-1]*1.1

plane = go.Surface(
        x=levels, 
        y=techs, 
        z=z_data,
        name="Salary by Tech Level")

fig.add_trace(
    plane,
    row=2,col=1
)

# fig = go.Figure(plane)

fig.update_layout(
    height=1500, 
    width=1800, 
    title_text="Market analysis",
    coloraxis=dict(colorscale='plasma'),
    showlegend=False,
    template="plotly_dark")

fig.show()

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([dcc.Dropdown(id='group-select', options=[{'label': i, 'value': i} for i in techs],
                           value='TOR', style={'width': '140px'})]),
    dcc.Graph('shot-dist-graph', config={'displayModeBar': False})])

@app.callback(
    Output('shot-dist-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(grpname):
    return go.Bar(
        x=tech_salary_offers_df['_id.tech'], 
        y=tech_salary_offers_df['salary_average'], 
        name="Salary by Tech",
        marker=dict(
            color=tech_salary_offers_df['salary_average'],
            coloraxis="coloraxis"
            )
        )
    # px.scatter(all_teams_df[all_teams_df.group == grpname], x='min_mid', y='player', size='shots_freq', color='pl_pps')


# app.layout = ddk.App(
#     [
#         ...
#         ddk.Card(
#             [
#                 ddk.CardHeader(title="Triggering Callbacks from Dash App & Host App"),
#                 ConsumerContext(id="clicks", path=["myObject", "clicks"]),
#                 ConsumerContext(id="data-one", path=["myObject", "data", "dataOne"]),
#                 ConsumerContext(id="data-two", path=["myObject", "data", "dataTwo"]),
#                 ...
#             ],
#             width=50,
#         ),
#         ddk.ControlCard(
#             [
#                 ddk.CardHeader(title="Triggering Host App Functions from Dash App"),
#                 ConsumerFunction(
#                     id="host-app-multiply", path=["myObject", "multiplyFunc"]
#                 ),
#                 ConsumerFunction(id="host-app-sum", path=["myObject", "sumFunc"]),
#                 ddk.ControlItem(...),
#                 ...
#             ],
#             width=50,
#         ),
#         ...
#     ]
# )


# Access the nested objects via `path=["myObject"]`
@app.callback(Output("display-full-object", "children"), Input("full-object", "value"))
def display(value):
    return json.dumps(value, indent=2)


# Access nested values via `path=[...]`
@app.callback(
    Output("display-data_dataOne_y[1]", "children"), Input("data_dataOne_y[1]", "value"))
def display(value):
    return "data.dataOne.y[1]={}".format(value)


# # Trigger Callback from Host App Data & Dash App Buttons
# @app.callback(
#     Output("plot", "figure"),
#     Input("update", "n_clicks"), Input("clicks", "value"),
#     State("data-one", "value"), State("data-two", "value"),
# )
# def update_figure(clicks_dash, clicks_host, trace1, trace2):
#     ...
#     return go.Figure(...)


# # Trigger Host App functions by sending data into the `params` property
# @app.callback(
#     Output("host-app-sum", "params"),
#     Input("sum", "n_clicks"),
#     State("input-x", "value"), State("input-y", "value"),
# )
# def trigger_sum(_, x, y):
#     return [x, y]
# ...

if __name__ == '__main__':
    app.run_server(debug=False)