import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install bs4
from fake_useragent import UserAgent  # pip install fake_useragent
from pprint import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

ua = UserAgent()
url = "https://cbr.ru"
headers = {"User-Agent": ua.chrome}
session = requests.session()  # аналогия с открытой вкладкой


date_102 = '2022-01-01'
url_102 = url + '/banking_sector/credit/coinfo/f102?regnum=354&dt=' + date_102

response = session.get(url_102, headers=headers)
soup_102 = BeautifulSoup(response.text, "html.parser")
s = '1. Финансовый результат после налогообложения'

def search_for_102_y(soup_102, date_from_data, search_string):
    value = 0
    value_positive = 0
    value_negative = 0

    if soup_102.find_all('tr'):
            # Находим строку с заголовком раздела
            # 1. Финансовый результат после налогообложения
        header_row = soup_102.find('td', string=search_string)
        if header_row:
            print(header_row)
                # Переходим к родительской строке и затем к следующей строке
            header_tr = header_row.find_parent('tr')
            if header_tr:
                next_row = header_tr.find_next_sibling('tr')
                if next_row:
                        # Извлекаем числовое значение из последней ячейки
                    cells = next_row.find_all('td', class_='right')
                    if cells:
                        last_cell = cells[-1]
                        if last_cell.text.strip():
                                # Очищаем текст от форматирования
                            value_positive = int(last_cell.text.replace('&nbsp;', '').replace(' ', '').replace('\xa0', ''))
                    next_next_row = next_row.find_next_sibling('tr')
                    if next_next_row:
                        cells = next_next_row.find_all('td', class_='right')
                        if cells:
                            last_cell = cells[-1]
                            if last_cell.text.strip():
                                    # Очищаем текст от форматирования
                                value_negative = int(last_cell.text.replace('&nbsp;', '').replace(' ', '').replace(
                                        '\xa0', ''))
                                value = value_positive - value_negative
    return value

print(search_for_102_y(soup_102,date_102,s))