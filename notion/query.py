from notion_client.helpers import collect_paginated_api
from notion_client import APIErrorCode, APIResponseError
from time import sleep
def GeneralErrorProcess(error):
    match error.code:
        case APIErrorCode.RateLimited:
            print("Rate Limited")
            sleep(60)
        case _:
            print(error)
            return False
    return False

def RetrieveDatabaseStructure(notion, database_id):
    try:
        result = notion.databases.retrieve(database_id=database_id).get("properties")
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return None
    return result

def UpdateDatabaseStructure(notion, database_id, properties):
    try:
        notion.databases.update(database_id=database_id,properties=properties)
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return False
    return True

def RetrieveDatabaseRows(notion, database_id, filter_properties=None):
    try:
        result = collect_paginated_api(notion.databases.query,
                                                 database_id=database_id,
                                                 filter_properties=filter_properties,
                                                 sort=[
                                                     {"timestamp":"last_edited_time",
                                                      "direction":"ascending"
                                                      }]
                                                 )
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return None
    return result

def RetrieveDatabaseList(notion, descending=True, cursor=None, page_size=100):
    try:
        database_results = collect_paginated_api(notion.search
                                                 ,query=""
                                                 ,next_cursor=cursor
                                                 ,filter={
                                                     "value": "database",
                                                     "property": "object"
                                                     }
                                                 ,sort={
                                                     "timestamp":"last_edited_time",
                                                     "direction": ("descending" if descending else "ascending")
                                                     }
                                                  ,page_size=page_size
                                                 )
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return None
    return database_results

def RetrieveList(notion, descending=True, cursor=None, page_size=100):
    try:
        results = collect_paginated_api(notion.search
                                                 ,query=""
                                                 ,start_cursor=cursor
                                                 ,sort={
                                                     "timestamp":"last_edited_time",
                                                     "direction": ("descending" if descending else "ascending")
                                                     }
                                                  ,page_size=page_size
                                                 )
    except APIResponseError as error:
        if error.code == APIErrorCode.ValidationError: ## cursor not found ignore
            return None
        GeneralErrorProcess(error)
        return None
    return results

def RetrieveLatestCursor(notion):
    try:
        result = notion.search(query=""
                               ,sort={
                                   "timestamp":"last_edited_time",
                                   "direction":"descending"
                                   }
                                   ,page_size=1
                                   ).get("results")
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return None
    return result[0].get("id")

def UpdatePageProperties(notion, page_id, properties):
    try:
        notion.pages.update(page_id=page_id,properties=properties)
    except APIResponseError as error:
        if error.code == APIErrorCode.ObjectNotFound:
            return False
        else:
            return False
    return True

def RetrievePage(notion, page_id, filter_properties=None):
    try:
        result = notion.pages.retrieve(page_id=page_id,filter_properties=filter_properties)
    except APIResponseError as error:
        GeneralErrorProcess(error)
        return None
    return result

