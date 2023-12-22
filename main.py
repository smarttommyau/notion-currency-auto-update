import os
import time
from dotenv import load_dotenv

load_dotenv()

# setup notion
from notion_client.helpers import collect_paginated_api
from notion_client import Client
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
    print("update values")
    for pageindex,(name,rate) in enumerate(rates.items()):
        print("page:",pageindex+1,"/",len(rates),name)
        if page_ids.get(name) is None:
            notion.pages.create(parent={"database_id":ID},properties={
                'Rate': {
                    'id': 'b%7DAM', 
                    'type': 'number', 
                    'number': rate
                    }, 
                'Name': {
                    'id': 'title', 
                    'type': 'title', 
                    'title': [{
                        'type': 'text', 
                        'text': {
                            'content': name,
                            'link': None
                            }, 
                        'annotations': {
                            'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'
                            },
                        'plain_text': name,
                        'href': None}
                              ]
                    }
                    })
        else:
            notion.pages.update(page_id=page_ids[name],properties={
                'Rate': {
                    'id': 'b%7DAM', 
                    'type': 'number', 
                    'number': rate
                    }, 
                })
        


