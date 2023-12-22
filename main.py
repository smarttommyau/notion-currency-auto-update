import os
import time
from dotenv import load_dotenv

load_dotenv()

# setup notion
from notion_client.helpers import collect_paginated_api
from notion_client import Client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

database_results = collect_paginated_api(notion.search,query="",filter={
        "value": "database",
        "property": "object"
    })
database_id = list()
for result in database_results:
    database_id.append(result.get("id"))
# get exchange rate details from https://github.com/fawazahmed0/currency-api
import requests

def getRate(From,To):
    transaction_url = ["https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/"+From+"/"+To+".min.json","https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/"+From+"/"+To+".json","https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+From+"/"+To+".min.json","https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest/currencies/"+From+"/"+To+".json"] # order to fallback
    for url in transaction_url:
        response = requests.get(url)
        match response.status_code:
            case 200:
                results = response.json()
                return results[To]
            case _:
                pass
    return 0

#retrieve databases
cache = dict[tuple[str,str],object]()
for dbindex,ID in enumerate(database_id):
    print("database:",dbindex+1,"/",len(database_id))
    database_struct = notion.databases.retrieve(database_id=ID).get("properties")
    propT = dict()
    propV = dict()
    db_prop = dict()
    for index,(prop,v) in enumerate(database_struct.items()):
        print("prop:",index+1,"/",len(database_struct), prop)
        if prop.startswith("ExRTT"):
            if str(v.get("type")) == "select":
                print("'",prop[5:],"'")
                propT[prop[5:]] = v
        elif prop.startswith("ExRTV"):
            if str(v.get("type")) == "number":
                print("'",prop[5:],"'")
                del v["name"]
                propV[prop[5:]] = v
            elif str(v.get("type")) == "formula":
                cur = prop.split()
                if len(cur)<2:
                    continue
                cur = cur[1].split(">")
                rate = 0
                if cache.get((cur[0],cur[1])) is None:
                    rate = getRate(cur[0],cur[1])
                    cache[(cur[0],cur[1])] = rate
                else:
                    rate = cache.get((cur[0],cur[1]))
                db_prop[prop] = v
                db_prop[prop]["formula"] = {
                        "type"  : "number",
                        "number": rate,
                        "expression": str(rate)
                        }  
                print(cur[0],">",cur[1],":",rate)
    if len(db_prop) > 0:
        notion.databases.update(database_id=ID,properties=db_prop)

    page_id = dict()
    print("Retrieve pageid and update")
    fulldatabase = collect_paginated_api(notion.databases.query, database_id=ID)
    for index,result in enumerate(fulldatabase):
        print("page:", index+1,"/",len(fulldatabase))
        properties = dict()
        for k,v in propT.items():
            if propV.get(k) is None or result.get("properties").get("ExRTT"+k).get("select") is None:
                continue
                
            cur = result.get("properties").get("ExRTT"+k).get("select").get("name")
            if cur is None:
                continue
            cur = cur.split(">")
            if len(cur)!= 2:
                continue
            rate = 0
            if cache.get((cur[0],cur[1])) is None:
                rate = getRate(cur[0],cur[1])
                cache[(cur[0],cur[1])] = rate
            else:
                rate = cache.get((cur[0],cur[1]))
            properties["ExRTV"+k] = propV.get(k)
            properties["ExRTV"+k]["number"] = rate
            print(cur[0],">",cur[1],":",rate)
        if len(properties) > 0:
            notion.pages.update(page_id=result.get("id"),properties=properties)
        


