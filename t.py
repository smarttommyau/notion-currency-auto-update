
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
database_id = []
for result in database_results:
    print(result.get("id"))
    database_id += result.get("id")
    

