from requests_html import HTMLSession
import pandas as pd


class Aliexpress:
    """
    This class can be used to search for keywords on aliexpress and scrape the data from the results.
    Contains: format_keyword(keyword), scraper(sample_size), run_scraper(keyword, sample_size), to_csv()
    """
    def __init__(self) -> None:
        self.__keyword = None
        self.__formatted_string = None
        self.__sample_size = None

    def format_keyword(self, keyword: str) -> str:
        '''
        formats the keyword and makes it appropriate for use
        :param keyword: keyword to be searched in aliexpress
        :return: formatted string
        '''
        self.__keyword = keyword
        self.__keyword = ''.join(e for e in self.__keyword if (e.isalnum() or e.isspace()))
        self.__keyword = self.__keyword.strip().lower()
        self.__formatted_string = self.__keyword.replace(" ", "+")
        return self.__formatted_string

    def scraper(self, sample_size: int, all_info=[], page=1) -> (str, pd.DataFrame):
        '''
        scrapes data from aliexpress search page
        :param sample_size: minimum size of data to fetch
        :param all_info: list of dictionaries of data scraped
        :param page: page number on the site
        :return: dataframe of the data scrapped
        '''
        self.__sample_size = sample_size
        url = f"https://www.aliexpress.com/wholesale?SearchText={self.__formatted_string}&page={page}"
        s = HTMLSession()
        r = s.get(url)
        r.html.render(sleep=1, scrolldown=10, timeout=20)
        products = r.html.find('div._1OUGS')
        print(f'Scrapping page {page}, number of items scrapped: {len(all_info)}, adding {len(products)} new items')

        for product in products:
            title = product.xpath('//div/div[1]/a/span')[0].text
            image_url = product.find('img.A3Q1M')[0].attrs['src']
            url = "www.aliexpress.com"+product.find('a._9tla3')[0].attrs['href']
            price = product.find('div._12A8D')[0].text
            store = product.find('a._2lsU7')[0].text
            item = {
                'category': self.__keyword,
                'name': title,
                'item_url': url,
                'image_url': image_url,
                'price': price,
                'store': store
                }
            all_info.append(item)

        if len(all_info) < sample_size and page < 60:
            page += 1
            try:
                self.scraper(sample_size, all_info, page)
            except:
                print(f'No more pages to scrape! Got {len(all_info)} products.')

        else:
            print(f'Gotten {len(all_info)} products!')

        df = pd.DataFrame(all_info)
        return df

    def to_csv(self, df: pd.DataFrame) -> None:
        '''
        used to save the dataframe to csv
        :param df: dataframe to be converted to csv
        :return: none
        '''
        df.to_csv(f'aliexpress_{self.__keyword}.csv', index=False)
        print(f'aliexpress_{self.__keyword}.csv file saved to folder')
        return

    def run_scraper(self, keyword: str, sample_size: int) -> (str, pd.DataFrame):
        '''
        used to call the format_keyword and scraper methods together
        :param keyword: keyword to be searched in aliexpress
        :param sample_size: minimum size of data to fetch
        :return: dataframe of data scrapped
        '''
        self.format_keyword(keyword)
        return self.scraper(sample_size)

