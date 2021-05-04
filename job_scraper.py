import re
import pprint
import pymongo
import feedparser
import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
import random
import configparser


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
        description_details = self.parse_single_description(offer)
        doc.update(description_details)
        if city not in self.cities:
            self.cities.append(city)
        if old_db_corresponding_record:
            collection.update_one({"id": offer['id']}, {"$set": doc})
        else:
            collection.insert_one(doc)

    def check_jji(self, collection: pymongo.collection.Collection, driver: webdriver.Chrome, new_only: bool = False):
        jji_feed = feedparser.parse('https://justjoin.it/feed.atom')
        for offer in tqdm.tqdm(jji_feed['entries']):
            old_db_corresponding_record = collection.find_one(
                {"id": offer['id']})
            if not (old_db_corresponding_record and new_only):
                self.update_single_offer(
                    collection, driver, offer, old_db_corresponding_record)

    def fix_all_descriptions(self, collection):
        """
            One time function to fix all descriptions
        """
        offers = collection.find()
        for offer in tqdm.tqdm(offers):
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


class Analyser():
    def __init__(self):
        pass

    def plot_cities(self, city_data):
        city_names = [doc["_id"] for doc in city_data]
        avg_wages = [int(doc["avg_pay"]) for doc in city_data]
        min_wages = [int(doc["min_pay"]) for doc in city_data]
        max_wages = [int(doc["max_pay"]) for doc in city_data]
        count = [float(doc["offers_count"]) for doc in city_data]
        count_scaled = [max(10, c/2) for c in count]
        colors = [random.random() for doc in city_data]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x=city_names, y=avg_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        ax.scatter(x=city_names, y=min_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        ax.scatter(x=city_names, y=max_wages,
                   s=count_scaled, c=colors, alpha=0.5)
        plt.xlabel("City")
        plt.ylabel("Average wage")
        plt.xticks(rotation=65)  # Rotates X-Axis Ticks by 45-degrees

        plt.show()

    def get_average_pay_by_city(self, collection: pymongo.collection.Collection, offer_threshold: int = 5):
        result = collection.aggregate(
            [
                {"$unwind": "$salary"
                 },
                {"$match": {
                    "salary.upper_range": {"$ne": "undisclosed"},
                    "salary.lower_range": {"$ne": "undisclosed"},
                }

                },
                {"$group":
                    {"_id": "$city",
                     "offers_count": {
                            "$sum": 1
                     },
                     "avg_pay": {
                         "$avg": {
                             "$toInt": "$salary.upper_range"
                         }
                     },
                     "max_pay": {
                         "$max": {
                             "$toInt": "$salary.upper_range"
                         }
                     },
                     "min_pay": {
                         "$min": {
                             "$toInt": "$salary.lower_range"
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
driver = webdriver.Chrome(options=options, executable_path={
                          config['selenium']['webdriver_path']})

myclient = pymongo.MongoClient(
    f"mongodb://{config['mongodb']['username']}:{config['mongodb']['password']}@{config['mongodb']['url']}/")  #
mydb = myclient["dev_job_scrapper"]
offers_collection = mydb["offers"]
scr = Scrapper()
scr.check_jji(offers_collection, driver, True)
# scr.fix_all_descriptions(offers_collection)
print("Finished Scrapping")
anal = Analyser()
city_data = anal.get_average_pay_by_city(offers_collection)
anal.plot_cities(city_data)
