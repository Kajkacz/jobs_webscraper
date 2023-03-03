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
from .settings import MONGO_DB_USER, MONGO_DB_PASSWORD
import pandas as pd

city_size_threshold = 20
tech_size_threshold = 50
tech_pipeline = [
    {"$unwind": "$salary"},
    {"$match": {"salary.average_pln": {"$ne": "undisclosed"}}},
    {"$match": {"salary.currency": "PLN"}},
    {"$unwind": "$skills"},
    {
        "$project": {
            "skills.skill_name": 1,
            "salary.average_pln": 1,
        }
    },
    {
        "$group": {
            "_id": {"tech": "$skills.skill_name"},
            "salary_average": {"$avg": "$salary.average_pln"},
            "tech_count": {"$count": {}},
        }
    },
    {"$match": {"tech_count": {"$gt": tech_size_threshold}}},
    {"$sort": {"salary_average": 1}},
]

levels = [
    # "nice to have",
    "junior",
    "regular",
    "advanced",
    "master",
]


# @login_required
def get_offers(request):
    # client = MongoClient(f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@localhost:27017/?authSource=admin&readPreference=primary&ssl=false&directConnection=true") # TODO Move password and username to env
    client = MongoClient(
        f"mongodb://scraper_root:super_secret_root_password@localhost:27017/?authSource=admin&readPreference=primary&ssl=false&directConnection=true"
    )
    db = client["dev_job_scrapper"]
    collection = db["offers"]
    threshold = 20
    mode = request.GET.get("mode")
    upper_threshold_count = int(
        request.GET.get("upper_threshold_count")
    )  
    lower_threshold_count = int(
        request.GET.get("lower_threshold_count")
    )  
    upper_threshold_cash = int(
        request.GET.get("upper_threshold_cash")
    )  
    lower_threshold_cash = int(
        request.GET.get("lower_threshold_cash")
    )  

    if mode == 'tech':
        tech_pipeline = [
            {"$unwind": "$salary"},
            {"$match": {
                "$and": [
                    {"salary.average_pln": {"$ne": "undisclosed"}},
                    {"salary.upper_range": {"$ne": "undisclosed"}},
                    {"salary.lower_range": {"$ne": "undisclosed"}},
                    {"salary.currency": "PLN"}
                ]
            }},
            {"$unwind": "$skills"},
            {
                "$project": {
                    "skills.skill_name": 1,
                    "salary.average_pln": 1,
                }
            },
            {
                "$group": {
                    "_id": {"tech": "$skills.skill_name"},
                    "salary_average": {"$avg": "$salary.average_pln"},
                    "tech_count": {"$count": {}},
                }
            },
            {
                "$match": {
                    "$and": [
                        {"tech_count": {"$lt": upper_threshold_count}},
                        {"tech_count": {"$gt": lower_threshold_count}},
                        {"salary_average": {"$lt": upper_threshold_cash}},
                        {"salary_average": {"$gt": lower_threshold_cash}},
                        {"salary_average": {"$ne": "nan"}},
                    ]
                }
            },
            {"$sort": {"salary_average": 1}},
        ]
        offers = collection.aggregate(tech_pipeline)
        offers_list = list(offers)
        tech_salary_offers_df = pd.json_normalize(offers_list)
        try:
            x = tech_salary_offers_df["_id.tech"].tolist()
            y = tech_salary_offers_df["salary_average"].tolist()
        except:
            x = []
            y = []
        return JsonResponse(
            {"x": x, "y": y, "offers_list": offers_list},
            content_type="application/json")
    elif mode =='cities':
        cities_pipeline = [
            {"$unwind": "$salary"},
            {"$match": {
                "$and": [
                    {"salary.average_pln": {"$ne": "undisclosed"}},
                    {"salary.upper_range": {"$ne": "undisclosed"}},
                    {"salary.lower_range": {"$ne": "undisclosed"}},
                    {"salary.currency": "PLN"}
                ]
            }},
            {
                "$project": {
                    "date": 1,
                    "city": 1,
                    "salary.average_pln": 1,
                }
            },
            {
                "$group": {
                    "_id": {"city": "$city"},
                    "salary_average": {"$avg": "$salary.average_pln"},
                    "city_count": {"$count": {}},
                }
            },
            {
                "$match": {
                    "$and": [
                        {"city_count": {"$lt": upper_threshold_count}},
                        {"city_count": {"$gt": lower_threshold_count}},
                        {"salary_average": {"$lt": upper_threshold_cash}},
                        {"salary_average": {"$gt": lower_threshold_cash}},
                        {"salary_average": {"$ne": "nan"}},
                    ]
                }
            },
            {"$sort": {"salary_average": 1}},
        ]
        offers = collection.aggregate(cities_pipeline)
        offers_list = list(offers)
        tech_salary_offers_df = pd.json_normalize(offers_list)
        try:
            x = tech_salary_offers_df["_id.city"].tolist()
            y = tech_salary_offers_df["salary_average"].tolist()
        except:
            x = []
            y = []
        return JsonResponse(
            {"x": x, "y": y, "offers_list": offers_list},
            content_type="application/json")
