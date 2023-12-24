# notion-currency-auto-update
Auto update currency exchange rate for notion database

# Installation
## By Python 
### Required packages
1. requests
2. notion-client
3. cachetools
> Run the below command to install <br>
`pip install requests notion-client cachetools`
### Optional packages
1. python-dotenv
   - This package is use to load environment variables from .env.<br>
     If you don't intend to use .env file, then this package is not required.
> Run the below command to install <br>
`pip install python-dotenv`
## By Docker
> Under development
# Usage
## By python
1. Get an **internal** integration token
   > Use Notion's [Getting Started Guide](https://developers.notion.com/docs/getting-started)
   > to get set up to use Notion's API.
2. Set the **NOTION_TOKEN** environment variable by setting it in `.env` or manually
3. Now, run `python main.py` to run the program everthing is set
## By Docker
> Under development
# 

# Future improvement
- [ ] use an currency api that refresh faster
# Acknowledge
- [ramnes/notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
- [fawazahmed0/currency-api](https://github.com/fawazahmed0/currency-api)
