import pandas as pd


def sp_500() -> [str, ]:
    return pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']


def russell_2000() -> [str, ]:
    return pd.read_html('https://stockmarketmba.com/stocksintherussell2000.php')[0]['Symbol']


def tsx() -> [str, ]:
    return pd.read_html('https://disfold.com/canada/companies/')[0]['Stock']
