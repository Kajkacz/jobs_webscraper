import pandas as pd
import dash
from dash import dcc,html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.subplots import make_subplots
import pymongo
import configparser

import pdmongo as pdm
import pandas as pd

# Get config definition
config = configparser.ConfigParser()
config.read('config.ini')

username = config['mongodb']['username']
password = config['mongodb']['password']
url = config['mongodb']['url']
prefix = "mongodb+srv"
db_name = config['mongodb']['db_name']
coll_name = config['mongodb']['collection_name']
rates_key = config['rates']['api_key']
mongo_url=f"{prefix}://{username}:{password}@{url}/{db_name}?retryWrites=true&w=majority"
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[db_name]
offers_collection = mydb[coll_name]
city_size_threshold = 20

cities_pipeline = [
    # {'$addFields': { 'date_formatted': { '$toDate': "$date" } } }, 
    # {'$match':{"date_formatted": {'$gte': 'ISODate("2021-06-01T00:00:00.0Z")'}}},
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

print(city_salary_offers_df.columns)
fig = make_subplots(rows=1, cols=2)

fig.add_trace(px.bar(city_salary_offers_df, x='_id.city', y='salary_average')
)

tech_size_threshold = 50

tech_pipeline = [
    # {'$addFields': { 'date_formatted': { '$toDate': "$date" } } }, 
    # {'$match':{"date_formatted": {'$gte': 'ISODate("2021-06-01T00:00:00.0Z")'}}},
    {'$unwind':'$salary'},
    {'$match':{"salary.average_pln":{"$ne" : "undisclosed"}}},
    {'$match':{"salary.currency":"PLN"}},
    {'$unwind':'$skills'},
    {'$project':{
        'skills.skill_name':1,#TODO add level
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

tech_salary_offers = offers_collection.aggregate(tech_pipeline)
tech_salary_offers_df = pd.json_normalize(list(tech_salary_offers))

# fig = px.bar(tech_salary_offers_df, x='_id.tech', y='salary_average')
fig.show()

# other fields:
# '_id':1,
# 'id':1,
# 'title':1,
# 'position':1,
# 'author':1,
# 'link':1,
# 'address':1,
# 'salary.average_pln':1,
# 'raw_salary':1,
# 'full_description':1,
# 'Company name':1,
# 'Company size':1,
# 'EXP lvl':1,
# 'description':1,
# 'skills':1
