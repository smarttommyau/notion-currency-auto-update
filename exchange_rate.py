if __name__ == "__main__":
    raise Exception("This not the main")
import requests
from cachetools import TLRUCache
from datetime import datetime, timedelta,timezone
class exchange_rate_getter:
    def __init__(self) -> None:
        self.cache = TLRUCache(maxsize=6550,timer=datetime.now,ttu=self.__myttu) #about 512kb
        self.date = "1990-1-1"
    def __myttu(self,_key,_value,now):
        return now + (datetime.strptime(self.date,"%Y-%m-%d").replace(tzinfo=timezone.utc) - datetime.now(timezone.utc) + timedelta(days=1,hours=2.5))
    def getRate(self,From:str,To:str) -> object:
        cache = self.cache.get((From,To)) 
        if cache is not None:
            return cache
# get exchange rate details from https://github.com/fawazahmed0/currency-api
        transaction_url = ["https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+From+"/"+To+".min.json","https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+From+"/"+To+".json"] # order to fallback, not using cdn as it is likely outdated
        for url in transaction_url:
            response = requests.get(url)
            match response.status_code:
                case 200:
                    results = response.json()
                    self.date = results["date"]
                    self.cache[(From,To)] = results[To]
                    return results[To]
                case _:
                    pass
        return 0
