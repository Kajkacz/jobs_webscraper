import random
import pymongo
import matplotlib.pyplot as plt

class Analyser():
    """Class to group the analysis layer of the application
    """
    def __init__(self, collection: pymongo.collection.Collection):
        """Init method 

        Args:
            collection (pymongo.collection.Collection): Mongo DB collection on which we want to conduct analysis
        """
        self.collection = collection
        self.prebuilt_pipeline_elements = {
            "match_no_undisclosed":{
                "$match": {
                "salary.upper_range_pln": {"$ne": "undisclosed"},
                "salary.lower_range_pln": {"$ne": "undisclosed"}}
                },
        }

    def plot_cities(self, city_data):
        """This method plots the data about cities min, max, average earnings with regard to sample size and plots it

        Args:
            city_data (List[Dict]) List of dictionaries with data from mongodb pipeline
        """
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
        """Filters the data to return top n offers in the system

        Args:
            limit (int, optional): Number of offers to be returned. Defaults to 10.
            ascending (bool, optional): Sets the order to ascending. Defaults to False.
            city_filter (str, optional): If passed, we restrict the results to the provided cities. Defaults to None.

        Returns:
            List: List of the top results
        """
        top_n_offers_aggregate = [
            {"$unwind": "$salary"},
            self.prebuilt_pipeline_elements["match_no_undisclosed"]
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
        """Gets the data about cities in system with min. offer_threshold of offers, like min, max and average wages

        Args:
            offer_threshold (int, optional): Cities with offers below this threshold will not be considered. Defaults to 5.

        Returns:
            List: Returns a list of results from MongoDB aggregation pipeline
        """
        result = self.collection.aggregate(
            [
                {"$unwind": "$salary"
                 },
                self.prebuilt_pipeline_elements["match_no_undisclosed"],
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
