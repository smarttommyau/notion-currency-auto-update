import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv unable to import, .env won't be loaded")

#setup currency exchamge getter
from exchange_rate import exchange_rate_getter
exchange_rate_getter = exchange_rate_getter()

# setup notion
from notion_client import  Client
if not os.getenv("NOTION_TOKEN"):
    raise SystemExit("NOTION_TOKEN not given")
notion = Client(auth=os.getenv("NOTION_TOKEN"))
    

from manager import manager
from datetime import datetime,timezone,timedelta
from time import sleep
manager = manager(notion,exchange_rate_getter)
manager.FullUpdate()
date = exchange_rate_getter.date
counts=0
print("Start monitoring!!!")
while True:
    if (datetime.strptime(date,"%Y-%m-%d").replace(tzinfo=timezone.utc) - datetime.now(timezone.utc) + timedelta(days=1,hours=2.5)) <= timedelta(): # Timer
        print("Time interval reached start update")
        manager.FullUpdate()
        date = exchange_rate_getter.date # Update Date
    counts = counts + 1 if not manager.Update() else 0# monitor change
    if not counts % 10: #show counter on each 10 runs
        print("No updates for {} runs".format(counts))
    sleep(2)


