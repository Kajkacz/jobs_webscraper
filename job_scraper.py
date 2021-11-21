import pymongo
import configparser

from scraper import Scraper
from rates_converter import RatesConverter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Get config definition
config = configparser.ConfigParser()
config.read('config.ini')

# Set up selenium webdriver
options = Options()
options.headless = True
options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
options.add_argument("--window-size=1920,1200")
options.add_argument('log-level=3')
driver = webdriver.Chrome(
    options=options, executable_path=config['selenium']['webdriver_path'])
local_db = False
# Connect to mongodb client
if local_db:
    username = config['mongodb']['local_username']
    password = config['mongodb']['local_password']
    url = config['mongodb']['local_url']
    prefix = "mongodb"
else:
    username = config['mongodb']['username']
    password = config['mongodb']['password']
    url = config['mongodb']['url']
    prefix = "mongodb+srv"

mongo_url=f"{prefix}://{username}:{password}@{url}/{config['mongodb']['db_name']}?retryWrites=true&w=majority"
print(f"Connecting to mongo at {mongo_url}")
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient[config['mongodb']['db_name']]
offers_collection = mydb[config['mongodb']['collection_name']]

# Run Scraper to get new offers
scr = Scraper()
scr.check_jji(offers_collection, driver, True)
# scr.fix_all_descriptions(offers_collection)
print("Finished Scrapping")

# Get current conversion rates
rates = RatesConverter(offers_collection.distinct(
    "salary.currency"), config['rates']['api_key'])
scr.convert_currencies(rates, offers_collection)
