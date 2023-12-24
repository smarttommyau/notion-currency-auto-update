if __name__ == "__main__":
    raise Exception("This not the main")
from notion_client import APIErrorCode, APIResponseError
from notion_client.helpers import collect_paginated_api

class notion_database:
    def __init__(self,notion,ID,exchange_rate_getter) -> None:
        self.notion = notion
        self.ID = ID
        self.propV = dict()
        self.propT = dict()
        self.propTf = list()
        self.filter_props = list()
        self.exchange_rate_getter = exchange_rate_getter
        self.success = self.PullPropertyStruct() & self.PropertyUpdate()

    def PullPropertyStruct(self) -> bool:
        try:
            self.struct = self.notion.databases.retrieve(database_id=self.ID).get("properties")
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                return False
            else:
                print(erroe)
                return False
        return True
    def PropertyUpdate(self) -> bool:
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
                    if v.get("name"):
                        del v["name"]
                    propV[prop[5:]] = v
                elif str(v.get("type")) == "formula":
                    cur = prop.split()
                    if len(cur)<2:
                        continue
                    cur = cur[1].split(">")
                    rate = self.exchange_rate_getter.getRate(cur[0],cur[1])
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
        propTf.sort()
        if propTf != self.propTf and len(db_prop) > 0:
            try:
                self.notion.databases.update(database_id=self.ID,properties=db_prop)
            except APIResponseError as error:
                if error.code == APIErrorCode.ObjectNotFound:
                    return False
                else:
                    print(error)
                    return False
        self.propTf = propTf
        # create the list of required props
        if propT == self.propT:
            return True
        self.cursor = None
        self.propT = propT
        self.propV = propV
        self.filter_props = list()
        for k,v in self.propT.items(): 
            self.filter_props.append(v.get("id"))
            self.filter_props.append(self.propV[k].get("id"))
        return True
    def UpdatePageWithResult(self,result,pageid) -> bool:
        properties = dict()
        for k in self.propT:
            if result.get("ExRTT"+k).get("select") is None:
                continue
                
            cur = result.get("ExRTT"+k).get("select").get("name")
            if cur is None:
                continue
            cur = cur.split(">")
            if len(cur)!= 2:
                continue
            rate = self.exchange_rate_getter.getRate(cur[0],cur[1])
            properties["ExRTV"+k] = self.propV.get(k)
            properties["ExRTV"+k]["number"] = rate
            print(cur[0],">",cur[1],":",rate)
        if len(properties) > 0:
            try:
                self.notion.pages.update(page_id=pageid,properties=properties)
            except APIResponseError as error:
                if error.code == APIErrorCode.ObjectNotFound:
                    return False
                else:
                    print(error)
                    return False
        return True
    def UpdatePage(self,pageid) -> bool:
        if len(self.filter_props) == 0:
            return True
        try:
            result = self.notion.pages.retrieve(pageid=pageid,filter_properties=self.filter_props)
        except APIResponseError as error:
            print(error)
            return False
        return self.UpdatePageWithResult(result,pageid)
    def UpdateAllPages(self) -> bool:
        if len(self.filter_props) == 0:
            return True
        try:
            fulldatabase = collect_paginated_api(self.notion.databases.query,
                                                 database_id=self.ID,
                                                 filter_properties=self.filter_props,
                                                 sort=[
                                                     {"timestamp":"last_edited_time",
                                                      "direction":"ascending"
                                                      }]
                                                 )
        except APIResponseError as error:
            if error.code == APIErrorCode.ObjectNotFound:
                return False
        need_retry = True
        for index,v in enumerate(fulldatabase):
            print("Page:",index+1,"/",len(fulldatabase))
            print(v.get("id"))
            need_retry &= self.UpdatePageWithResult(v.get("properties"),v.get("id"))
        if not need_retry:
            self.PullPropertyStruct()
            self.PropertyUpdate()
            self.UpdateAllPages()

        return True

