import pandas as pd
from string import ascii_uppercase

def sp_500() -> [str, ]:
    return list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])


def russell_2000() -> [str, ]:
    print("!!!")
    results = []
    for char in ascii_uppercase:
        results += list(pd.read_html
                        (f'https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({char})')
                        [0]['Symbol'])
    return results


def tsx() -> [str, ]:
    return pd.read_html('https://disfold.com/canada/companies/')[0]['Stock']
