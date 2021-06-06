import pymongo
import configparser

from analyser import Analyser

# Get config definition
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to mongodb client
myclient = pymongo.MongoClient(
    f"mongodb+srv://{config['mongodb']['username']}:{config['mongodb']['password']}@{config['mongodb']['url']}/{config['mongodb']['db_name']}?retryWrites=true&w=majority")  #
mydb = myclient[config['mongodb']['db_name']]
offers_collection = mydb[config['mongodb']['collection_name']]

# Run analysis for our data
anal = Analyser(offers_collection)
city_data = anal.get_average_pay_by_city()
top_offers = anal.get_top_n_offers(city_filter="Warszawa")
for off in top_offers:
    print(off['link'])
anal.plot_cities(city_data)
