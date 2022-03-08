import re
import tqdm
import pymongo
import feedparser
from bs4 import BeautifulSoup

from typing import Dict
from selenium import webdriver

from rates_converter import RatesConverter

class Scraper():
    """Class for scrapping the web for joboffers
    """

    def __init__(self):
        """Init method
        """
        self.cities = []
        self.currencies = []
        self.cities_translations = {'Warsaw': 'Warszawa'}
        self.failed_sites = []

    def __del__(self):
        if self.failed_sites:
            print("Failed sites : ")
            for s in self.failed_sites:
                print(s)

    def get_salary_details(self, salary, salaries_raw):
        """Get's the salary details from the salary chunk

        Args:
            salary (str): String with salary info from JJI
            salaries_raw (str): 

        Raises:
            IndexError: Raises IndexError when IndexError is thrown and the salary is not 'undisclosed'

        Returns:
            Dict: chunk with the salary data
        """
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
        """Parses the info for a single offer

        Args:
            collection (pymongo.collection.Collection): MongoDB collection to run the update against
            driver (webdriver.Chrome): Selenium webdriver to get offer details
            offer (dict): A single offer from MongoDB
            old_db_corresponding_record (Dict, optional): Corresponding record in MongoDB, if exists. Defaults to None.
        """
        
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
        resp = driver.get(offer['id'])
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
            print(f'Error parsing description for offer {offer["id"]} : {e}')
        if city not in self.cities:
            self.cities.append(city)
        if old_db_corresponding_record:
            collection.update_one({"id": offer['id']}, {"$set": doc})
        else:
            collection.insert_one(doc)

    def check_jji(self, collection: pymongo.collection.Collection, driver: webdriver.Chrome, new_only: bool = False):
        """Run a check for new offers in JustJoin.it RSS feed

        Args:
            collection (pymongo.collection.Collection): MongoDB collection to be updated
            driver (webdriver.Chrome): Selenium webdriver for getting offer details
            new_only (bool, optional): If passed we only get new offers and ignore any updates on those in the system. Defaults to False.
        """
        jji_feed = feedparser.parse('https://justjoin.it/feed.atom')
        for offer in tqdm.tqdm(jji_feed['entries'], desc="Getting new offers"):
            old_db_corresponding_record = collection.find_one(
                {"id": offer['id']})
            if not (old_db_corresponding_record and new_only):
                self.update_single_offer(
                    collection, driver, offer, old_db_corresponding_record)

    def fix_all_descriptions(self, collection: pymongo.collection.Collection):
        """One time function to fix all descriptions

        Args:
            collection (pymongo.collection.Collection): MongoDB collection to be updated
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
        """Gets the description details for a single offer

        Args:
            offer (Dict): MongoDB single offer

        Returns:
            Dict: Updated data from description
        """
        description = offer["full_description"]
        try:
            descr_intro, descr_rest = description.split("More filters\n")
        except ValueError as e:
            self.failed_sites.append(offer)
            return ""
        company_descr = descr_rest.split("Tech stack")[0]
        descr_rest = "Tech stack".join(descr_rest.split("Tech stack")[1:])
        tech_stack_description = descr_rest.split("Description")[0]
        descr_rest = "Description".join(descr_rest.split("`Description`")[1:])
        tech_stack = list(filter(None, tech_stack_description.split('\n')))
        descr_text = descr_rest.split("Apply")
        descr_garbage = descr_text[-1]
        descr_text = "Apply".join(descr_text[:-2])
        skill_list = [{"skill_name": skill.replace('.', ''), "skill_level": level} for (skill, level) in zip(*[
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
        """Maps the wages to PLN currencies for all offers in DB - we run it on all offers to adjust for currency fluctuation

        Args:
            rates (RatesConverter): RatesConverter instance to convert
            collection (pymongo.collection.Collection): MongoDB collection to be updated
        """
        def map_single_salary_field(salary: Dict, salary_field: str, currency_rate: float):
            """Helper method to convert a single field - adds a new field with _pln ending

            Args:
                salary (Dict): nested document with salary info
                salary_field (str): name of the salary field
                currency_rate (float): Currency rate from target currency to PLN

            Returns:
                Dict: Updated salary chunk
            """
            if salary[salary_field] != 'undisclosed':
                salary[salary_field] = int(salary[salary_field])
                salary[f'{salary_field}_pln'] = int(int(
                    salary[salary_field]) * currency_rate)
            else:
                salary[f'{salary_field}_pln'] = 'undisclosed'
            return salary

        def map_single_salary(salary: Dict, currency_rate: float):
            """Maps all fields in a single salary field

            Args:
                salary (Dict): nested document with salary info
                currency_rate (float): Currency rate from target currency to PLN

            Returns:
                Dict: Updated salary chunk
            """
            salary = map_single_salary_field(salary,'upper_range' , currency_rate)
            salary = map_single_salary_field(salary,'lower_range' , currency_rate)
            if salary['upper_range'] != 'undisclosed':
                salary['average'] = (salary['upper_range'] + salary['lower_range'])/2
            else:
                salary['average'] = 'undisclosed'
            salary = map_single_salary_field(salary,'average' , currency_rate)
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
