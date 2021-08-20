from src.scraper.aliexpress_scraper import Aliexpress
from src.database.database import Database


sample = Aliexpress()
df_m_shoes = sample.run_scraper('dog', 2000)
sample.to_csv(df_m_shoes)

sample_db = Database()
sample_db.insert_data(df_m_shoes)
db_m_shoes = sample_db.select_data('dog')
print(db_m_shoes.head(20))