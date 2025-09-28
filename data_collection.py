import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install bs4
from fake_useragent import UserAgent  # pip install fake_useragent
from pprint import pprint
ua = UserAgent()
# print(ua.random)


# url = "https://cbr.ru/finorg/foinfo/reports/?ogrn=1027700167110"
url = "https://cbr.ru"

# headers = {"User-Agent": ua.random}
headers = {"User-Agent": ua.chrome}
params = {"ogrn": "1027700167110"}
session = requests.session()  # аналогия с открытой вкладкой
response = session.get(url + "/finorg/foinfo/reports", params=params, headers=headers)


# print(response.status_code) # проверка ответа

soup = BeautifulSoup(response.text, "html.parser")
test_link = soup.find_all("a", {'class': 'versions_item', 'title': 'Включая обороты'})
# Метод find()/ find_all() ожидает:
# Первый параметр - имя тега
# Второй параметр - словарь с атрибутами (или именованные параметры)

# print(test_link)
href_101 = []
for row in test_link:
    href_101.append(row.get('href'))

# Дата для фильтрации
cutoff_date = '2008-06-01' # отбросим 101 форму до этой даты, покольку нет итога баланса банка

# Фильтрация ссылок
filtered_href = [url for url in href_101 if url.split('dt=')[1] >= cutoff_date]

# сделать функцию по очистке soup

def search_for_101(soup_101, list_of_accounts):
    '''
    Функция производит поиск и суммирование счетов из формы 101
    '''
    amount_of_accounts = []
    for account in list_of_accounts:

        target_row = None
        for row in soup_101.find_all('tr'):
            first_cell = row.find('td')
            if first_cell and first_cell.getText().strip() == account:
                target_row = row

        # Если нашли нужную строку, извлекаем последнюю непустую ячейку
        if target_row:
            # Находим все ячейки с классом 'right hover' в этой строке
            cells = target_row.find_all('td', class_='right')

            # Ищем последнюю непустую ячейку
            last_non_empty_cell = None
            for cell in cells:
                if cell.text.strip():  # если ячейка не пустая (cell.text - получение текстового содержимого,
                                                                # .strip() - удаление пробелов в начале и конце)
                    last_non_empty_cell = cell

            if last_non_empty_cell:
                # Извлекаем и очищаем текст
                raw_text = last_non_empty_cell.text
                amount_of_accounts.append(int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', '')))

    return sum(map(int, amount_of_accounts))

data =[]
for link in filtered_href:
    url_101 = url + link
    response_101 = session.get(url_101, headers=headers)
    soup_101 = BeautifulSoup(response_101.text, "html.parser")
    print()
    # поиск итога баланса (x4)
    row_x4 = soup_101.find('tr', class_='italic')
# if row:
    # Все ячейки с классом right
    cells = row_x4.find_all('td', class_='right')
    # Последняя ячейка (индекс -1)
    last_cell = cells[-1] if cells else None
# if last_cell and last_cell.text.strip():
    x4 = last_cell.text.replace(' ', '').replace('\xa0', '').replace(' ', '')

    # поиск х8 - кредитный портфель (45.0 + 45.2)

    # Находим строку, где первая ячейка содержит текст "45.0"
    target_row = None
    for row in soup_101.find_all('tr'):
        first_cell = row.find('td')
        if first_cell and first_cell.getText().strip() == '45.0':
            target_row = row
            print(row)
            break

    # Если нашли нужную строку, извлекаем последнюю непустую ячейку
    if target_row:
        # Находим все ячейки с классом 'right hover' в этой строке
        cells = target_row.find_all('td', class_='right')

        # Ищем последнюю непустую ячейку
        last_non_empty_cell = None
        for cell in cells:
            if cell.text.strip():  # если ячейка не пустая
                last_non_empty_cell = cell

        if last_non_empty_cell:
            # Извлекаем и очищаем текст
            raw_text = last_non_empty_cell.text
            x8_45_0 = int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', ''))
            x8_45_1 = 0
        else:
            x8_45_0 = 0
    else:
        target_row = None
        for row in soup_101.find_all('tr'):
            first_cell = row.find('td')
            if first_cell and first_cell.getText().strip() == '45.1':
                target_row = row
                print(row)
                break

        # Если нашли нужную строку, извлекаем последнюю непустую ячейку
        if target_row:
            # Находим все ячейки с классом 'right hover' в этой строке
            cells = target_row.find_all('td', class_='right')

            # Ищем последнюю непустую ячейку
            last_non_empty_cell = None
            for cell in cells:
                if cell.text.strip():  # если ячейка не пустая
                    last_non_empty_cell = cell

            if last_non_empty_cell:
                # Извлекаем и очищаем текст
                raw_text = last_non_empty_cell.text
                x8_45_1 = int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', ''))
                x8_45_0 = 0

    x8 = x8_45_0 + x8_45_1

    data.append({
        "date": link.split('dt=')[1],
        "x4": x4,
        "x8": x8})
    print(data)