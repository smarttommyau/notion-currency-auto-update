<h1 align="center"> notion-currency-auto-update</h1>

![european-union-1493894_1280](https://github.com/smarttommyau/notion-currency-auto-update/assets/75346987/37859e82-7876-490c-ad10-ea8f108dc4b6)
<br>  
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/smarttommyau/notion-currency-auto-update)
![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)<br>  
**Auto update currency exchange rate for Notion**


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
> [Docker hub repo](https://hub.docker.com/r/smarttommyau/notion-currency-auto-update)
### Build locally
`docker build .`
### Pull image
`docker pull smarttommyau/notion-currency-auto-update`
# Usage
1. Setup and Run Environment
2. Connect Notion
## By python
1. Get an **internal** integration token
   > Use Notion's [Getting Started Guide](https://developers.notion.com/docs/getting-started)
   > to get set up to use Notion's API.
2. Set the **NOTION_TOKEN** environment variable by setting it in `.env` or manually
3. Now, run `python main.py` to run the program 
## By Docker
Simply Run `docker run smarttommyau/notion-currency-auto-update`
> `--env-file .env` to load .env file
> `-d` to run in background
## Setup Notion
- First, connect the integration to the database by add connection
- Then, follow the below instructions
> You may also refer to this [TEMPLATE](https://dramatic-porpoise-b92.notion.site/c21c60a4d7b142a99a44c95c1b8d46f5?v=d952a5f9e6e045a8af23e33c7f0545d2&pvs=4) 
### Ways To Use(Formula) 
> This way all rows in this column will be the same
1. Create a new column in type of formula
2. Naming scheme
`ExRTV currencyA>CurrencyB AnyName`
- ExRTV is a required prefix
- CurrencyA: From this currency
- CurrencyB: target currency
- AnyName: whatever you like
### Way To Use(Select with Number)
1. Create 2 new columns one is a **select** and one is a **number**
> Not multi-select!!
2. For the select, Naming Scheme: 
`ExRTT AnyName`
- **ExRTT** is a required prefix
- AnyName: whatever you like
3. For the number, Naming Scheme:
`ExRTV AnyName`
- **ExRTV** is a required prefix
- AnyName: whatever you like
4. For any row, set the select to in format of
`CurrencyA>CurrencyB`
- CurrencyA: From this currency
- CurrencyB: target currency
5. Then, the ExRTV field will be auto update
# Future improvement
- [ ] use an currency api that refresh more frequently
- [ ] Host the public integration version
# Note
> It is normal that the update is not instantaneously due to indexing time and limited acess rate of the notion api. 

# Acknowledge
- [ramnes/notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
- [fawazahmed0/currency-api](https://github.com/fawazahmed0/currency-api)
