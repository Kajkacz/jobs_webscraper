import json
import requests
from typing import List

class RatesConverter():
    """ Get's the currency exchange rate for provided 
    """
    def __init__(self, currency_list: List[str], access_key: str):
        self.currency_rates = self.get_rates(currency_list, access_key)

    def __getitem__(self, key: str):
        """Allows for the dict-like access to the currency exchange rates

        Args:
            key (str): 3 letter string with currency identifier

        Returns:
            float: currency exchange rate from the key currency
        """
        return self.currency_rates[key]

    def get_rates(self, currency_list: List[str],  access_key: str, base_currency: str = 'PLN'):
        """Gets the current exchange rates using the fixer.io api

        Args:
            currency_list (List[str]): List of currency codes for which we want to get the currency rates
            access_key (str): Access key to the fixer.io API
            base_currency (str, optional): Currency to be used as base currency. We can't get it directly from fixer on free plan so we will calculate it ourselves. Defaults to 'PLN'.

        Returns:
            Dict: Dictionary with currency codes as keys and exchange rates as values
        """
        if base_currency not in currency_list:
            currency_list.append(base_currency)
        rates_url = f"http://data.fixer.io/api/latest?access_key={access_key}&symbols={','.join(currency_list)}"
        response = requests.get(rates_url)  # TODO Add error handling
        raw_response_json = json.loads(response.text)
        our_base_to_query_base = 1/raw_response_json['rates'][base_currency]
        return {k: 1/(v*our_base_to_query_base)
                for k, v in raw_response_json['rates'].items()}
