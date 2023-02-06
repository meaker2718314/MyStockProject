import pandas as pd
from string import ascii_uppercase as asc_u
import random
def sp_500() -> [str, ]:
    return pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']


def russell_1000() -> [str, ]:
    return pd.read_html('https://en.wikipedia.org/wiki/Russell_1000_Index')[2].iloc[:, [1]]['Ticker']


def tsx() -> [str, ]:
    return pd.read_html('https://disfold.com/canada/companies/')[0]['Stock']
