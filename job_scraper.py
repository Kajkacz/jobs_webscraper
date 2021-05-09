import re
import requests
import pprint
import pymongo
import feedparser
import tqdm
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import List, Dict
import matplotlib.pyplot as plt
import random
import configparser


class RatesConverter():

    def __init__(self, currency_list: List[str], access_key: str):
        self.currency_rates = self.get_rates(currency_list, access_key)

    def __getitem__(self, key: str):
        return self.currency_rates[key]

    def get_rates(self, currency_list: List[str],  access_key: str, base_currency: str = 'PLN'):
        if base_currency not in currency_list:
            currency_list.append(base_currency)
        rates_url = f"http://data.fixer.io/api/latest?access_key={access_key}&symbols={','.join(currency_list)}"
        response = requests.get(rates_url)  # TODO Add error handling
        raw_response_json = json.loads(response.text)
        our_base_to_query_base = 1/raw_response_json['rates'][base_currency]
        return {k: 1/(v*our_base_to_query_base)
                for k, v in raw_response_json['rates'].items()}


class Scrapper():

    def __init__(self):
        self.cities = []
        self.currencies = []
        self.cities_translations = {'Warsaw': 'Warszawa'}

    def get_salary_details(self, salary, salaries_raw):
        salary_chunk = {}
        try:
            salary_chunk["currency"] = re.findall(
                "[A-Z][A-Z][A-Z]", salary)[0]
        except Exception:
            salary_chunk["currency"] = 'PLN'
        if len(re.findall("\(.{1,15},.{1,15}\)", salaries_raw)) > 0:
            salary_chunk["employment_type"] = "Permanent"
        else:
            salary_chunk["employment_type"] = re.findall(
                "\(.*", salary)[0].replace("(", "").replace(")", "")
        try:
            salary_chunk["lower_range"] = salary.split('-')[0]
            salary_chunk["upper_range"] = re.findall(
                "\d*", salary.split('-')[1])[0]
        except IndexError:
            if 'undisclosed' in salary:
                salary_chunk["lower_range"] = salary_chunk["upper_range"] = 'undisclosed'
            else:
                raise IndexError
        return salary_chunk

    def update_single_offer(self, collection: pymongo.collection.Collection, driver: webdriver.Chrome, offer: dict, old_db_corresponding_record=None):
        doc = {
            "id": offer['id'],
            "date": offer['published'],
            "title": offer['title'],
            "position": offer['title'].split('@')[0],
            "author": offer['author'],
            "link": offer['link'],
        }
        offer_soup = BeautifulSoup(offer.summary, 'html.parser')
        text = offer_soup.text.split('\n')
        address = text[5].split('Location: ', 1)[1]
        city = address.split(',')[-1].strip()
        address = ','.join(address.split(',')[:-1])
        salaries_raw = text[4].split('Salary: ')[1]
        salaries = [salaries_raw] if len(re.findall(
            "\(.{1,17},.{1,17}\)", salaries_raw)) > 0 else salaries_raw.split(',')
        salary_ranges = []
        for salary in salaries:
            salary_ranges.append(
                self.get_salary_details(salary.replace(" ", ""), salaries_raw))

        if city in self.cities_translations:
            city = self.cities_translations[city]
        driver.get(offer['id'])
        page_text = driver.find_element_by_id('root')

        doc["address"] = address
        doc["city"] = city
        doc["salary"] = salary_ranges
        doc["raw_salary"] = salaries_raw
        doc["full_description"] = page_text.text
        offer["full_description"] = page_text.text
        try:
            description_details = self.parse_single_description(offer)
            doc.update(description_details)
        except IndexError as e:
            print(f'Error parsing description : {e}')
        if city not in self.cities:
            self.cities.append(city)
        if old_db_corresponding_record:
            collection.update_one({"id": offer['id']}, {"$set": doc})
        else:
            collection.insert_one(doc)

    def check_jji(self, collection: pymongo.collection.Collection, driver: webdriver.Chrome, new_only: bool = False):
        jji_feed = feedparser.parse('https://justjoin.it/feed.atom')
        for offer in tqdm.tqdm(jji_feed['entries'], desc="Getting new offers"):
            old_db_corresponding_record = collection.find_one(
                {"id": offer['id']})
            if not (old_db_corresponding_record and new_only):
                self.update_single_offer(
                    collection, driver, offer, old_db_corresponding_record)

    def fix_all_descriptions(self, collection: pymongo.collection.Collection):
        """
            One time function to fix all descriptions
        """
        offers = collection.find()
        for offer in tqdm.tqdm(offers, desc="Fixing the descriptions"):
            try:
                description_details = self.parse_single_description(offer)
                collection.update_one({"id": offer['id']}, {
                    "$set": description_details})
            except IndexError:
                print("ERROR")

    def parse_single_description(self, offer):
        description = offer["full_description"]
        descr_intro, descr_rest = description.split("More filters\n")
        company_descr = descr_rest.split("Tech stack")[0]
        descr_rest = "Tech stack".join(descr_rest.split("Tech stack")[1:])
        tech_stack_description = descr_rest.split("Description")[0]
        descr_rest = "Description".join(descr_rest.split("Description")[1:])
        tech_stack = list(filter(None, tech_stack_description.split('\n')))
        descr_text = descr_rest.split("Apply")
        descr_garbage = descr_text[-1]
        descr_text = "Apply".join(descr_text[:-2])
        skill_list = [{skill.replace('.', ''): level} for (skill, level) in zip(*[
            iter(tech_stack)]*2)]

        company_descr = company_descr.split(offer['author'])[1].split('\n')
        company_descr[0] = offer['author']
        company_descr = list(
            filter(None, company_descr))
        description_result = {prop.replace('.', ''): value for (value, prop) in zip(*[
            iter(company_descr)]*2) if prop != "Added"}
        description_result.update({
            "description": descr_text,
            "skills": skill_list
        })
        return description_result

    def convert_currencies(self, rates: RatesConverter, collection: pymongo.collection.Collection):
        def map_single_salary_field(salary: Dict, salary_field: str, currency_rate: float):
            if salary[salary_field] != 'undisclosed':
                salary[salary_field] = int(salary[salary_field])
                salary[f'{salary_field}_pln'] = int(int(
                    salary[salary_field]) * currency_rate)
            else:
                salary[f'{salary_field}_pln'] = 'undisclosed'
            return salary

        def map_single_salary(salary: Dict, currency_rate: float):
            salary = map_single_salary_field(salary,'upper_range' , currency_rate)
            salary = map_single_salary_field(salary,'lower_range' , currency_rate)
            return salary


        offers=collection.find()
        for offer in tqdm.tqdm(offers, desc = "Mapping the currencies to PLN"):
            try:
                new_salaries=[]
                for salary in offer["salary"]:
                    new_salaries.append(map_single_salary(salary, rates[salary['currency']]))
                collection.update_one({"id": offer['id']}, {
                                      "$set": {"salary":new_salaries}})
            except IndexError:
                print("ERROR converting currencies")


class Analyser():
    def __init__(self, collection: pymongo.collection.Collection):
        self.collection = collection

    def plot_cities(self, city_data):
        city_names=[doc["_id"] for doc in city_data]
        avg_wages=[int(doc["avg_pay"]) for doc in city_data]
        min_wages=[int(doc["min_pay"]) for doc in city_data]
        max_wages=[int(doc["max_pay"]) for doc in city_data]
        count=[float(doc["offers_count"]) for doc in city_data]
        count_scaled=[max(10, c/2) for c in count]
        colors=[random.random() for doc in city_data]
        fig, ax=plt.subplots(figsize = (10, 6))
        ax.scatter(x = city_names, y = avg_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        ax.scatter(x=city_names, y=min_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        ax.scatter(x=city_names, y=max_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        plt.xlabel("City")
        plt.ylabel("Average wage")
        plt.xticks(rotation=65)

        plt.show()

    def get_top_n_offers(self, limit:int = 10, ascending = False, city_filter :str = None):
        top_n_offers_aggregate = [
            {"$unwind": "$salary"},
            {"$match": {
                "salary.upper_range_pln": {"$ne": "undisclosed"},
                "salary.lower_range_pln": {"$ne": "undisclosed"},
            }}
        ]
        if city_filter:
            top_n_offers_aggregate.append(
            {"$match": {
                "city":city_filter
            }
            })
        top_n_offers_aggregate.extend([
            {"$sort": {"salary.upper_range_pln": 1 if ascending else -1}},
            {"$limit":limit},
            {"$project":{"link" :1}}
        ])
        result = self.collection.aggregate(top_n_offers_aggregate)
        return list(result)

    def get_average_pay_by_city(self, offer_threshold: int = 5):
        result = self.collection.aggregate(
            [
                {"$unwind": "$salary"
                 },
                {"$match": {
                    "salary.upper_range_pln": {"$ne": "undisclosed"},
                    "salary.lower_range_pln": {"$ne": "undisclosed"},
                }
                },
                {"$group":
                    {"_id": "$city",
                     "offers_count": {
                            "$sum": 1
                     },
                     "avg_pay": {
                         "$avg": {
                             "$toInt": "$salary.upper_range_pln"
                         }
                     },
                     "max_pay": {
                         "$max": {
                             "$toInt": "$salary.upper_range_pln"
                         }
                     },
                     "min_pay": {
                         "$min": {
                             "$toInt": "$salary.lower_range_pln"
                         }
                     },
                     }
                 },
                {"$match": {
                    "offers_count": {"$gte": offer_threshold}
                }
                },
                {
                    "$sort": {"avg_pay": 1}
                }
            ]
        )
        return list(result)


config = configparser.ConfigParser()
config.read('config.ini')
options = Options()
options.headless = True
options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(
    options=options, executable_path=config['selenium']['webdriver_path'])

myclient = pymongo.MongoClient(
    f"mongodb://{config['mongodb']['username']}:{config['mongodb']['password']}@{config['mongodb']['url']}/")  #
mydb = myclient["dev_job_scrapper"]
offers_collection = mydb["offers"]
scr = Scrapper()
# scr.check_jji(offers_collection, driver, True)
# scr.fix_all_descriptions(offers_collection)
print("Finished Scrapping")
rates = RatesConverter(offers_collection.distinct(
    "salary.currency"), config['rates']['api_key'])
scr.convert_currencies(rates, offers_collection)
anal = Analyser(offers_collection)
city_data = anal.get_average_pay_by_city()
top_offers = anal.get_top_n_offers(city_filter="Warszawa")
# for off in top_offers:
#     print(off['link'])
anal.plot_cities(city_data)
