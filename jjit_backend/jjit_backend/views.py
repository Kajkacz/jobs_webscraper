from rest_framework_mongoengine import viewsets
from .serializers import OfferSerializer
from .models import Offer
import json
class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from django.contrib.auth.decorators import login_required
from .settings import MONGO_DB_USER,MONGO_DB_PASSWORD


city_size_threshold = 20
tech_size_threshold = 50
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

levels = [
    # "nice to have",
    "junior",
    "regular",
    "advanced",
    "master"
    ] 

# @login_required
def get_offers(request):
    # client = MongoClient(f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@localhost:27017/?authSource=admin&readPreference=primary&ssl=false&directConnection=true") # TODO Move password and username to env
    client = MongoClient(f"mongodb://scraper_root:super_secret_root_password@localhost:27017/?authSource=admin&readPreference=primary&ssl=false&directConnection=true")
    db = client["dev_job_scrapper"]
    collection = db["offers"]
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
        {'$match':{"tech_count":{"$gt":tech_size_threshold}}},
        {'$sort':{"salary_average":1}},
    ]
    offers = collection.aggregate(tech_pipeline_w_level)
    return JsonResponse( list(offers), safe=False)