if __name__ == "__main__":
    raise Exception("This not the main")
from notion import notion_database
from notion.query import RetrieveList, RetrieveDatabaseList, RetrieveLatestCursor
class manager:
    def __init__(self,notion,exchange_rate_getter) -> None:
        self.notion = notion
        self.exchange_rate_getter = exchange_rate_getter
        self.cursor = None
        self.databases = dict[str,notion_database]()
    def FullUpdate(self):
        # Reset databases
        self.databases = dict[str,notion_database]()
        # Collect all database
        database_results = RetrieveDatabaseList(self.notion)
        if database_results is None:
            return
        for dbindex,result in enumerate(database_results): # Loop through each database to update values
            print("database:",dbindex+1,"/",len(database_results))
            database = notion_database(self.notion,result.get("id"),self.exchange_rate_getter)
            if database.success:
                self.databases[result.get("id")] = database
                database.UpdateAllPages()
        self.cursor = RetrieveLatestCursor(self.notion)
    def Update(self) -> bool:
        # Collect updated databases
        results = RetrieveList(self.notion, descending=False ,cursor=self.cursor,page_size=5)
        if results is None:
            return False
        # Update cursor
        self.cursor  = results[-1].get("id")
        page_list = list() # for pages, process after db updated
        updated_db = list() # skip updated db to prevent recursive running update on same item
        for index,result in enumerate(results):
            pageid = result.get("id")
            if result.get("object") == "database" :
                print("Items:",index+1,"/",len(results)) # print only if it is processed
                if self.databases.get(pageid) is None:
                    database = notion_database(self.notion,result.get("id"),self.exchange_rate_getter)
                    if database.success:
                        self.databases[pageid] = database
                        database.UpdateAllPages()
                        updated_db.append(pageid)
                        self.cursor = pageid
                else:
                    if self.databases[pageid].PullPropertyStruct() & self.databases[pageid].PropertyUpdate():
                        self.databases[pageid].UpdateAllPages()
                        updated_db.append(pageid)
                        self.cursor = pageid

            else:
                dbid = result.get("parent").get("database_id")
                if dbid is not None:
                    page_list.append((dbid,result.get("properties"),pageid))
        updated = False
        for index,(dbid,prop,pageid) in enumerate(page_list):
            if dbid in updated_db:
                continue
            db = self.databases.get(dbid)
            if db is not None:
                result = db.UpdatePageWithResult(prop,pageid)
                if result is None:
                    continue
                if not result:
                    db.PullPropertyStruct()
                    db.PropertyUpdate()
                    db.UpdateAllPages()
                else:
                    self.cursor = pageid
                updated = True
            print("Pages:",index+1,"/",len(page_list)) # print only if it is processed
        return updated
            
