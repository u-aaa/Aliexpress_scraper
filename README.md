# Aliexpress Scraper
## Description
This project was designed to scrape data from Aliexpress search page and upload the data to a postgres database.
The information collected are listed below.
* Name - this is the name of the product
* Item_url - this is the link (url) to the item on aliexpress
* Image_url - this is the link (url) to the image used to list the item
* Price - this is the price at which the item was listed
* Store - this is the name of the aliexpress store listing the product

## Technologies
* [Python 3.8](https://www.python.org/) - Base programming language used.
* [Postgres Database](https://www.postgresql.org/) - Database used to store data scraped.

## Getting started
To use this scrapper, first install all the required packages from the ```requirements.txt``` file. 
For security reasons, the postgres database information is saved in a ```database.ini``` file. 
This file should be added to the database folder before using the scraper. The ```database.ini``` file should look like this
```
[postgresql]
host=host
database=database
user=user
password=password
port=port
```

## Usage
The project consists of two classes - Aliexpress and Database. The ```Aliexpress``` class is used to get scrape data 
using a search phrase (keyword) and minimum number of products required.
The ```Database``` class inserts the data into tables in a postgres database.
You can run the scraper and add it to the postgres database using the main.py file as shown below

```python
from src.scraper.aliexpress_scraper import Aliexpress
from src.database.database import Database

sample = Aliexpress()
df_m_shoes = sample.run_scraper('male shoes', 1000)
sample.to_csv(df_m_shoes)

sample_db = Database()
sample_db.insert_data(df_m_shoes)
db_m_shoes = sample_db.select_data('male shoes')
print(db_m_shoes.head(20))
```

## License
The MIT License - Copyright (c) 2021 - Blessing Ehizojie-Philips