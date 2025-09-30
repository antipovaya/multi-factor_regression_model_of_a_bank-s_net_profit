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



target_td = soup_102.find('td', string='Итого по разделу 1')
if target_td:
    print(target_td, date_102, 'target_td')
    header_row = target_td.parent

else:
    print("не найдено", date_102)
    # # Метод.parent в BeautifulSoup возвращает родительский элемент текущего тега.
    # # soup.find('td', class_='hover', string='Итого по разделу 1') - находит элемент < td > с нужным текстом
    # # .parent - поднимается на один уровень вверх по дереву к родительскому элементу
    # # Извлекаем все числовые ячейки в строке
if header_row:
    header_td = header_row.find_all('td', class_='right')
    # Берём последнюю ячейку и получаем текст
    last_cell = header_td[-1].get_text(strip=True).replace('&nbsp;', '').replace(' ', '')
    print(last_cell, date_102)

print('2022-12-01' >= '2022-01-01')