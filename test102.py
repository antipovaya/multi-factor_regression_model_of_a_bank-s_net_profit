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

# https://cbr.ru/banking_sector/credit/coinfo/f102?regnum=354&dt=2025-08-01
date_102 = '2025-08-01'
# url_102 = url + '/banking_sector/credit/coinfo/f102?regnum=354&dt=' + date_102
# params = {"dt": "2025-09-01"}

# response = session.get(url_102, headers=headers)
# soup_102 = BeautifulSoup(response.text, "html.parser")
print()


while date_102 >= '2008-06-01':
    url_102 = url + '/banking_sector/credit/coinfo/f102?regnum=354&dt=' + date_102
    response = session.get(url_102, headers=headers)
    soup_102 = BeautifulSoup(response.text, "html.parser")
    if soup_102.find_all('tr') and date_102 > '2022-12-01':
        # Находим строку с заголовком раздела
        header_row = soup_102.find('td', string=re.compile(r'Раздел 1\. Процентные расходы'))
        if header_row:
            # Переходим к родительской строке и затем к следующей строке
            header_tr = header_row.find_parent('tr')
            # Что делает find_parent():
            # Находит родительский элемент указанного типа
            # 'tr' - ищет родительский тег < tr >
            # Возвращает всю строку таблицы, содержащую найденную ячейку
            if header_tr:
                next_row = header_tr.find_next_sibling('tr')
                # Что делает find_next_sibling():
                # Находит следующий элемент того же уровня
                # 'tr' - ищет следующий тег < tr >
                # Возвращает следующую строку таблицы
                if next_row:
                    # Извлекаем числовое значение из последней ячейки
                    cells = next_row.find_all('td', class_='right')
                    if cells:
                        last_cell = cells[-1]
                        if last_cell.text.strip():
                            # Очищаем текст от форматирования
                            value = last_cell.text.replace('&nbsp;', '').replace(' ', '')
                            print(f"Найдено значение: {value} на {date_102}")
        elif date_102 <= '2022-12-01':
            # Находим строку с нужным текстом
            target_td = soup_102.find('td', string='Итого по разделу 1')

            if target_td:
                header_row = target_td.parent

            else:
                print("не найдено", date_102)
            # Метод.parent в BeautifulSoup возвращает родительский элемент текущего тега.
            # soup.find('td', class_='hover', string='Итого по разделу 1') - находит элемент < td > с нужным текстом
            # .parent - поднимается на один уровень вверх по дереву к родительскому элементу
            # Извлекаем все числовые ячейки в строке
            if header_row:
                header_td = header_row.find_all('td', class_='right')
                print(header_td)

                # Берём последнюю ячейку и получаем текст
                last_cell = header_td[-1].get_text(strip=True).replace('&nbsp;', '').replace(' ', '')
                print(last_cell, date_102)
            else:
                print("не найдено", date_102)
    # Преобразуем строку в объект datetime
    current_date = datetime.strptime(date_102, '%Y-%m-%d')

    # Уменьшаем на 1 месяц
    prev_month = current_date - relativedelta(months=1)

    # Преобразуем обратно в строку
    prev_month_str = prev_month.strftime('%Y-%m-%d')
    date_102 = prev_month_str