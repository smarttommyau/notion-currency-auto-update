if __name__ == "__main__":
    raise Exception("This not the main")
from notion_client.helpers import collect_paginated_api
from notion import APIResponseError, notion_database
from datetime import datetime
class manager:
    def __init__(self,notion,exchange_rate_getter) -> None:
        self.notion = notion
        self.exchange_rate_getter = exchange_rate_getter
        self.cursor = None
        self.last_edit = datetime.min
        self.databases = dict[str,notion_database]()
    def FullUpdate(self):
        # Reset databases
        self.databases = dict[str,notion_database]()
        # Collect all database
        try:
            database_results = collect_paginated_api(self.notion.search
                                                 ,query=""
                                                 ,filter={
                                                     "value": "database",
                                                     "property": "object"
                                                     }
                                                 ,sort={
                                                     "timestamp":"last_edited_time",
                                                     "direction":"descending"
                                                     }
                                                 )
        except APIResponseError as error:
            print(error)
            return
        if len(database_results) > 1: # Get cursor if length >= 2, as cursor get errors on using latest cursor
            self.cursor  = database_results[1].get("id")
        if len(database_results) > 0: # get last edited time
            self.last_edit = datetime.fromisoformat(str(database_results[0].get("last_edited_time")))

        for dbindex,result in enumerate(database_results): # Loop through each database to update values
            print("database:",dbindex+1,"/",len(database_results))
            database = notion_database(self.notion,result.get("id"),self.exchange_rate_getter)
            if database.success:
                self.databases[result.get("id")] = database
                database.UpdateAllPages()
    def Update(self) -> bool:
        # Collect updated databases
        try:
            database_results = collect_paginated_api(self.notion.search
                                                 ,query=""
                                                 ,next_cursor=self.cursor
                                                 ,sort={
                                                     "timestamp":"last_edited_time",
                                                     "direction":"ascending"
                                                     }
                                                ,filter={
                                                    "value": "database",
                                                    "property": "object"
                                                    }
                                                ,page_size=5
                                                 )
        except APIResponseError as error:
            print(error)
            return False
        # skip process if no updted
        if not len(database_results) or datetime.fromisoformat(str(database_results[-1].get("last_edited_time"))) == self.last_edit:
            return False
        # Update cursor if needed
        if len(database_results) > 1:
            self.cursor  = database_results[1].get("id")
        page_list = list() # for pages, process after db updated
        updated_db = list() # skip updated db to prevent recursive running update on same item
        for index,result in enumerate(database_results):
            if datetime.fromisoformat(str(result.get("last_edited_time"))) <= self.last_edit:
                continue
            print("Items:",index+1,"/",len(database_results))
            pageid = result.get("id")
            if result.get("object") == "database" :
                if self.databases.get(pageid) is None:
                    database = notion_database(self.notion,result.get("id"),self.exchange_rate_getter)
                    if database.success:
                        self.databases[pageid] = database
                        database.UpdateAllPages()
                        updated_db.append(pageid)
                else:
                    if self.databases[pageid].PullPropertyStruct() & self.databases[pageid].PropertyUpdate():
                        self.databases[pageid].UpdateAllPages()
                        updated_db.append(pageid)

            else:
                dbid = result.get("parent").get("database_id")
                if dbid is not None:
                    page_list.append((dbid,result.get("propertiesself.last"),pageid))

        # Update last edit
        self.last_edit = datetime.fromisoformat(database_results[0].get("last_edited_time"))

        for index,(dbid,prop,pageid) in enumerate(page_list):
            print("Pages:",index+1,"/",len(page_list))
            if dbid in pageid:
                continue
            db = self.databases.get(dbid)
            if db is not None:
                if not db.UpdatePageWithResult(prop,pageid):
                    db.PullPropertyStruct()
                    db.PropertyUpdate()
                    db.UpdateAllPages()
        return True
            
