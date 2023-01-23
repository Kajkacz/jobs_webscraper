import sys
import os
import pymongo
import configparser

from scraper import Scraper
from rates_converter import RatesConverter
from boto.s3.connection import S3Connection

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up selenium webdriver
options = Options()
options.headless = True
options.add_argument('log-level=3')

suffix = "?retryWrites=true&w=majority"
# Get config definition
if os.path.exists('config.ini'):
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    options.add_argument("--window-size=1920,1200")
    config = configparser.ConfigParser()
    config.read('config.ini')
    if len(sys.argv) > 1:
        local_db = sys.argv[1]
    else:
        local_db = config['mongodb']['local_db'] == 'True'
    driver = webdriver.Chrome(
        options=options, executable_path=config['selenium']['webdriver_path'])
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
else:
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)
    prefix = "mongodb+srv"
    url=  os.environ['mongo_url']
    username  =  os.environ['mongo_username']
    password =       os.environ['mongo_password']
    db_name =   os.environ['mongo_db_name']
    coll_name = os.environ['mongo_coll_name']
    rates_key = os.environ['rates_key']
mongo_url=f"{prefix}://{username}:{password}@{url}/{db_name}{suffix}"
print(f"Connecting to mongo at {mongo_url}")
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[db_name]
offers_collection = mydb[coll_name]

# Run Scraper to get new offers
scr = Scraper()
scr.check_jji(offers_collection, driver, True)
# scr.fix_all_descriptions(offers_collection)
print("Finished Scrapping")

# Get current conversion rates
rates = RatesConverter(offers_collection.distinct(
    "salary.currency"), rates_key)
scr.convert_currencies(rates, offers_collection) #TODO Change this to only convert new offers
