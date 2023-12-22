import os
import time
from dotenv import load_dotenv

load_dotenv()

# setup notion
from notion_client import Client
from notion_client.helpers import collect_paginated_api
notion = Client(auth=os.getenv("NOTION_TOKEN"))


database_id = ["e9df0ad6658642229b3928f0ccf9e4bb"] # list of databases id to be updated

# get transaction details from https://github.com/fawazahmed0/currency-api
import requests
currency = "hkd"

transaction_url = ["https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/"+currency+".min.json","https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/"+currency+".json","https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+currency+".min.json","https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+currency+".json"] # order to fallback
# url select the currency you are using to replace the url
rates = dict()

for url in transaction_url:
    response = requests.get(url)
    match response.status_code:
        case 200:
            results = response.json()
            rates = results[currency]
            break
        case _:
            pass

#retrieve databases
for dbindex,ID in enumerate(database_id):
    print("database:",dbindex+1,"/",len(database_id))
    page_id = dict()
    print("Retrieve pageid")
    fulldatabase = collect_paginated_api(notion.databases.query, database_id=ID,filter_properties=["title"])
    page_ids = dict()
    for result in fulldatabase:
        name = ""
        for key,prop in result.get("properties").items():
            if prop["type"] == "title":
                name = key
        print(result.get("properties").get(name).get("title")[0].get("plain_text"), result.get("id"))
        page_ids[result.get("properties").get(name).get("title")[0].get("plain_text")] = result.get("id")
    for k,v in rates.items():
        print(page_ids[k],k)
