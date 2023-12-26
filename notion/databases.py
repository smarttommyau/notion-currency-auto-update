if __name__ == "__main__":
    raise Exception("This not the main")
from .query import   RetrieveDatabaseStructure,\
                    UpdateDatabaseStructure,  \
                    UpdatePageProperties,     \
                    RetrievePage,              \
                    RetrieveDatabaseRows

class notion_database:
    def __init__(self,notion,ID,exchange_rate_getter) -> None:
        self.notion = notion
        self.ID = ID
        self.propV = dict()
        self.propT = dict()
        self.propTf = list()
        self.filter_props = list()
        self.exchange_rate_getter = exchange_rate_getter
        self.success = self.PullPropertyStruct() & (self.PropertyUpdate() in (None,True))

    def PullPropertyStruct(self) -> bool:
        temp = RetrieveDatabaseStructure(self.notion,self.ID)
        if temp is None:
            return False
        self.struct = temp
        return True
    
    def PropertyUpdate(self) -> bool:
        # Process properties
        propV = dict()
        propT = dict()
        db_prop = dict()
        propTf = list()
        struct = self.struct
        for index,(prop,v) in enumerate(struct.items()):
            print("prop:",index+1,"/",len(struct), prop)
            if prop.startswith("ExRTT"):
                if str(v.get("type")) == "select":
                    print("'",prop[5:],"'")
                    propT[prop[5:]] = v
            elif prop.startswith("ExRTV"):
                if str(v.get("type")) == "number":
                    print("'",prop[5:],"'")
                    # Delete name field if exist
                    if v.get("name"):
                        del v["name"]
                    propV[prop[5:]] = v
                elif str(v.get("type")) == "formula":
                    cur = prop.split() # split to get the second part of prop name
                    if len(cur)<2:
                        continue
                    cur = cur[1].split(">") # split to get currency names
                    if len(cur)!= 2:
                        continue
                    # Obtain rate
                    rate = self.exchange_rate_getter.getRate(cur[0],cur[1])
                    # skip if rate is equal
                    if rate == v.get("formula").get("number") or str(rate) == v.get("formula").get("expression"):
                        continue
                    # Update properties
                    propTf.append(prop)
                    db_prop[prop] = v
                    db_prop[prop]["formula"] = {
                            "type"  : "number",
                            "number": rate,
                            "expression": str(rate)
                            }  
                    print(cur[0],">",cur[1],":",rate)
        propT = {k:propT[k] for k in propV} # clean all irrelevant fields
        # Update formulas
        propTf.sort() # sort to match last propTf
        updated = False
        if len(db_prop) > 0: # check if update is needed
            updated = True
            if not UpdateDatabaseStructure(self.notion,self.ID,db_prop):
                return False

        self.propTf = propTf # Update propTf

        # create the list of required props
        if propT == self.propT: # check if update is needed
            return True
        self.cursor = None # reset cursor
        # Update propT and propV and filter_props
        self.propT = propT
        self.propV = propV
        self.filter_props = list()
        for k,v in self.propT.items(): 
            self.filter_props.append(v.get("id"))
            self.filter_props.append(self.propV[k].get("id"))
        if not updated:
            return None
        return True

    def UpdatePageWithResult(self,result,pageid) -> bool:
        properties = dict()
        for k in self.propT:
            # check if type is select, or RTV is number, if not skip
            if  result.get("ExRTT"+k) is None or result.get("ExRTV"+k) is None or \
                result.get("ExRTT"+k).get("type") != "select" or \
                result.get("ExRTT"+k).get("select") is None or \
                result.get("ExRTV"+k).get("type") != "number": 
                continue
                
            cur = result.get("ExRTT"+k).get("select").get("name")
            if cur is None:
                continue
            cur = cur.split(">") # split to get currency names
            if len(cur)!= 2:
                continue
            # Obtain rate
            rate = self.exchange_rate_getter.getRate(cur[0],cur[1])
            # skip if rate is equal
            if rate == result.get("ExRTV"+k).get("number"):
                continue
            # Update properties
            properties["ExRTV"+k] = self.propV.get(k)
            properties["ExRTV"+k]["number"] = rate
            print(cur[0],">",cur[1],":",rate)
        if len(properties) > 0:
            return UpdatePageProperties(self.notion,pageid,properties)
        return None
    
    def UpdatePage(self,pageid) -> bool:
        if len(self.filter_props) == 0:
            return True
        result = RetrievePage(self.notion,pageid,self.filter_props)
        if result is None:
            return False
        return self.UpdatePageWithResult(result,pageid)
    def UpdateAllPages(self) -> bool:
        if len(self.filter_props) == 0:
            return True
        fulldatabase = RetrieveDatabaseRows(self.notion,self.ID,self.filter_props)
        if fulldatabase is None:
            return False
        need_retry = True
        for index,v in enumerate(fulldatabase):
            print("Page:",index+1,"/",len(fulldatabase))
            print(v.get("id"))
            need_retry &= self.UpdatePageWithResult(v.get("properties"),v.get("id")) in (None,True)
        if not need_retry:
            self.PullPropertyStruct()
            self.PropertyUpdate()
            self.UpdateAllPages()

        return True
