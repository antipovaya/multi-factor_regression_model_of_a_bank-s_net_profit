import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install bs4
from fake_useragent import UserAgent  # pip install fake_useragent
from pprint import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta

ua = UserAgent()



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

href_101 = []
for row in test_link:
    href_101.append(row.get('href'))

# Дата для фильтрации
cutoff_date = '2008-06-01' # отбросим 101 форму до этой даты, покольку нет итога баланса банка

# Фильтрация ссылок
filtered_href = [url for url in href_101 if url.split('dt=')[1] >= cutoff_date]


def search_for_101(soup_101, list_of_accounts):
    '''
    Функция производит поиск активных счетов и их суммирование из формы 101
    '''
    amount_of_accounts = []
    for account in list_of_accounts:

        target_row = None
        for row in soup_101.find_all('tr'):
            first_cell = row.find('td')
            # if first_cell and first_cell.getText().strip() == account:
            # Если мы дошли до строки "Итого по активу (баланс)", то выходим из цикла, поскольку дальше будут пассивные счета
            if first_cell:
                cell_text = first_cell.getText().strip()
                if cell_text == "Итого по активу (баланс)":
                    break
                # Если в этой строке мы нашли нужный account, то сохраняем и выходим
                if account in cell_text:
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
                print(int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', '')))
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
    if row_x4:
        # Все ячейки с классом right
        cells = row_x4.find_all('td', class_='right')
        # Последняя ячейка (индекс -1)
        last_cell = cells[-1] if cells else None
        # if last_cell and last_cell.text.strip():
        x4 = last_cell.text.replace(' ', '').replace('\xa0', '').replace(' ', '')
    else:
        x4 = 0

    # поиск х8 - кредитный портфель (45.0 + 45.2)
    if link.split('dt=')[1] < '2023-01-01':
        x8 = search_for_101(soup_101, ['44101', '44102', '44103', '44104', '44105', '44106', '44107',
                                       '44108', '44109', '44201', '44202', '44203', '44204', '44205', '44206', '44207',
                                       '44208', '44209', '44210', '44301', '44302', '44303', '44304', '44305', '44306',
                                       '44307', '44308', '44309', '44310', '44401', '44402', '44403', '44404', '44405',
                                       '44406', '44407', '44408', '44409', '44410', '44501', '44503', '44504', '44505',
                                       '44506', '44507', '44508', '44509', '44601', '44603', '44604', '44605', '44606',
                                       '44607', '44608', '44609', '44701', '44703', '44704', '44705', '44706', '44707',
                                       '44708', '44709', '44801', '44803', '44804', '44805', '44806', '44807', '44808',
                                       '44809', '44901', '44903', '44904', '44905', '44906', '44907', '44908', '44909',
                                       '45001', '45003', '45004', '45005', '45006', '45007', '45008', '45009', '45101',
                                       '45103', '45104', '45105', '45106', '45107', '45108', '45109', '45201', '45203',
                                       '45204', '45205', '45206', '45207', '45208', '45209', '45301', '45303', '45304',
                                       '45305', '45306', '45307', '45308', '45309', '45401', '45403', '45404', '45405',
                                       '45406', '45407', '45408', '45409', '45410', '45502', '45503', '45504', '45505',
                                       '45506', '45507', '45508', '45509', '45510', '45523', '45524', '45601', '45602',
                                       '45603', '45604', '45605', '45606', '45607', '45608', '45701', '45702', '45703',
                                       '45704', '45705', '45706', '45707', '45708', '45709'])
        x9 = search_for_101(soup_101, ['45801', '45802', '45803', '45804', '45805', '45806', '45807',
                                       '45808', '45809', '45810', '45811', '45812', '45813', '45814', '45815', '45816',
                                       '45817', '45901', '45902', '45903', '45904', '45905', '45906', '45907', '45908',
                                       '45909', '45910', '45911', '45912', '45913', '45914', '45915', '45916', '45917'])
    else:
        x8 = search_for_101(soup_101, ["45.0", "45.1", "45.2"])

        x9 = search_for_101(soup_101, ['458', '459'])


    data.append({
        "date": link.split('dt=')[1],
        "x1": 0,
        "x2": 0,
        "x3": 0,
        "x4": x4,
        "x8": x8,
        "x9": x9,
        "x5": 0,
        "x6": 0,
        "x7": 0,
        "y": 0})

