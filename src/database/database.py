import pandas as pd
import psycopg2
from src.database.config import config
import psycopg2.extras as extras

class Database:
    '''
    Pushes data from the aliexpress scraper to a postgres database
    Contains: create_category_tb(), create_products_tb(), create_tables(), drop_table(tablename), insert_category(df),
            insert_products(df), insert_data(df), select_data(keyword), to_csv(df, file_name), close()
    '''
    def __init__(self):
        params = config()
        self.__conn = psycopg2.connect(**params)
        self.__cur = self.__conn.cursor()

    def create_category_tb(self) -> None:
        '''
        creates the category table
        :return:
        '''
        create_cat_tb = ''' 
            CREATE TABLE IF NOT EXISTS category(
            id INT GENERATED ALWAYS AS IDENTITY,
            name varchar(255) NOT NULL UNIQUE,
            PRIMARY KEY(id)
        );
        '''
        self.__cur.execute(create_cat_tb)
        self.__conn.commit()
        print('Category table created!')
        return

    def create_products_tb(self) -> None:
        '''
        creates the product table
        :return: none
        '''
        create_products = '''
        CREATE TABLE IF NOT EXISTS products(
            id INT GENERATED ALWAYS AS IDENTITY,
            name varchar(255),
            item_url varchar(255),
            image_url varchar(255),
            price varchar(255),
            store varchar(255),
            cat_id INT NOT NULL,                                   
            PRIMARY KEY(id),
            CONSTRAINT category_id 
                FOREIGN KEY(cat_id)
                REFERENCES category(id)
        );
        '''
        self.__cur.execute(create_products)
        self.__conn.commit()
        print('Products table created!')
        return

    def create_tables(self) -> None:
        '''
        used to call the create_category_tb and create_products_tb together
        :return: none
        '''
        self.create_category_tb()
        self.create_products_tb()
        return

    def drop_table(self, tablename: str):
        '''
        used to drop a table in the database
        :param tablename: table to be dropped
        :return: table deleted
        '''
        drop_tb = "DROP TABLE %s;" % tablename

        try:
            self.__cur.execute(drop_tb)
            self.__conn.commit()
            print(f"{tablename} table deleted")
        except psycopg2.errors.UndefinedTable:
            self.__conn.rollback()
            print(f'{tablename} table does not exist in the database')

    def insert_category(self, df: pd.DataFrame) -> int:
        '''
        inserts keyword to the category table
        :param df: dataframe of data to be inserted
        :return: cat_id of keyword inserted
        '''
        key_word = df.loc[0, 'category']
        try:
            self.__cur.execute("INSERT INTO category (name) VALUES (%s)", (key_word,))
            self.__conn.commit()
            count = self.__cur.rowcount
            print(count, f"record inserted successfully into the category table - {key_word})")
        except psycopg2.errors.UniqueViolation:
            print(f'{key_word} already exists in the category table')
            self.__cur.execute("ROLLBACK")
            self.__conn.commit()

        self.__cur.execute("SELECT * FROM category where name = %s", (key_word,))
        cat_id = self.__cur.fetchone()[0]
        return cat_id

    def insert_products(self, cat_id: int, df: pd.DataFrame) -> None:
        '''
        used to insert product list to the products table
        :param cat_id: category id
        :param df: dataframe to be inserted
        :return: insert completed
        '''
        df = df.drop('category', axis=1)
        df['cat_id'] = cat_id
        tuples = [tuple(x) for x in df.to_numpy()]
        cols = ','.join(list(df.columns))
        insert_query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s,%%s,%%s,%%s)" % ('products', cols)
        print('Inserting data to products table..')

        try:
            extras.execute_batch(self.__cur, insert_query, tuples, len(df))
            self.__conn.commit()
            print(f'Insert completed. {len(df)} records were inserted.')
        except psycopg2.DatabaseError as error:
            print("Error: %s" % error)
            self.__conn.rollback()
        return

    def insert_data(self, df) -> None:
        '''
        calls the insert_category and insert_product methods together
        :param df: dataframe to be inserted to the database
        :return: none
        '''
        cat_id = self.insert_category(df)
        self.insert_products(cat_id, df)
        return

    def select_data(self, keyword: str) -> pd.DataFrame:
        '''
        fetches data from database using keyword
        :param keyword: category name
        :return: select result as dataframe
        '''
        select_query = '''
        select category.name, products.id, products.name, item_url, image_url, price, store
        from products 
        LEFT JOIN category on products.cat_id = category.id
        WHERE category.name = '%s'
        ''' % (keyword,)
        self.__cur.execute(select_query)
        df = pd.DataFrame(self.__cur.fetchall(), columns= ('category', 'product_id', 'product_name', 'product_url',
                                                           'image_url', 'price', 'store'))
        return df

    def to_csv(self, df: pd.DataFrame, file_name: str) -> None:
        '''
        saves a dataframe as csv file
        :param df: dataframe to be saved as csv file
        :param file_name: name of csv file
        :return: none
        '''
        df.to_csv(f'db_{file_name}.csv', index=False)
        print(f'db_{file_name}.csv file saved to folder')

    def close(self) -> None:
        '''
        used to close the database connection
        :return: none
        '''
        self.__cur.close()
        self.__conn.close()
        return
