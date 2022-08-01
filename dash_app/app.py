import pandas as pd
import dash
from dash import dcc,html
from dash.dependencies import Input, Output
import plotly.express as px
import pymongo
import configparser

import pdmongo as pdm
import pandas as pd

# Get config definition
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to mongodb client
all_offers_df = pdm.read_mongo(config['mongodb']['collection_name'], [{'$project':{'_id':1,'id':1,'date':1,'title':1,'position':1,'author':1,'link':1,'address':1,'city':1,'salary':1,'raw_salary':1,'full_description':1,'Company name':1,'Company size':1,'EXP lvl':1,'description':1,'skills':1,'Brand Story':1}},{'$unwind':'$salary'}], f"mongodb+srv://{config['mongodb']['username']}:{config['mongodb']['password']}@{config['mongodb']['url']}/{config['mongodb']['db_name']}?retryWrites=true&w=majority")
print(all_offers_df.columns)
fig = px.bar(all_offers_df, x='city', y='salary')
fig.show()
