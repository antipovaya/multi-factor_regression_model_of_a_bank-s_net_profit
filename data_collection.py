import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install bs4
from fake_useragent import UserAgent  # pip install fake_useragent
import pandas as pd


ua = UserAgent()
url = "https://cbr.ru"
headers = {"User-Agent": ua.chrome}
params = {"ogrn": "1027700167110"}
session = requests.session()  # аналогия с открытой вкладкой
response = session.get(url + "/finorg/foinfo/reports", params=params, headers=headers)
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
    """
    Функция производит поиск активных счетов и их суммирование из формы 101

    :param soup_101: Распарсенный HTML/XML документ формы 101
    :param list_of_accounts: Банковские счета, которые нужно суммировать

    """
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
                # print(int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', '')))
                amount_of_accounts.append(int(raw_text.replace(' ', '').replace('\xa0', '').replace(' ', '')))

    return sum(map(int, amount_of_accounts))


def search_for_102(soup_102, date_from_data, search_string_1_period, search_string_2_period, chapter):
    """
    Функция производит поиск разделов доходов или расходов в форме 102.

    :param soup_102: Распарсенный HTML/XML документ формы 102.
    :param date_from_data: Дата отчета.
    :param search_string_1_period: Строка поиска для формы 102 с 2023 года
    :param search_string_2_period Строка поиска для формы 102 до 2023 года
    :param chapter Строка поиска раздела для формы 102 до 2023 года
    """
    # Инициализируем value значением по умолчанию
    value = 0

    if date_from_data > '2022-12-01':
        if soup_102.find_all('tr'):
            # Находим строку с заголовком раздела
            header_row = soup_102.find('td', string=search_string_1_period)
            if header_row:
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
                                value = last_cell.text.replace('&nbsp;', '').replace(' ', '').replace('\xa0', '')
    else:
        section_header = soup_102.find('td', string=chapter)
        if section_header:
            section_tr = section_header.find_parent('tr')
            if section_tr:
                # Ищем все последующие строки после заголовка раздела
                current_row = section_tr
                found_total = False

                # Проходим по всем следующим строкам, пока не найдем "Итого по разделу 1"
                while current_row and not found_total:
                    current_row = current_row.find_next_sibling('tr')
                    if current_row:
                        # Проверяем, содержит ли текущая строка "Итого по разделу 1"
                        total_td = current_row.find('td', string=search_string_2_period)
                        if total_td:
                            # Нашли строку с итогом, извлекаем числовые ячейки
                            numeric_cells = current_row.find_all('td', class_='right')
                            if numeric_cells:
                                value = (numeric_cells[-1].get_text(strip=True).replace('&nbsp;', '').
                                         replace(' ', '').replace('\xa0', ''))
                            found_total = True

    return value


def search_for_102_y(soup_102, search_string):
    """
    Функция производит поиск финансового результата в форме 102.

    :param soup_102: Распарсенный HTML/XML документ формы 102.
    :param search_string: Строка поиска (заголовок раздела).

    """
    value = 0
    value_positive = 0
    value_negative = 0
    if soup_102.find_all('tr'):
        # Находим строку с заголовком раздела
        # 1. Финансовый результат после налогообложения
        header_row = soup_102.find('td', string=search_string)
        if header_row:
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
                            value_positive = int(
                                last_cell.text.replace('&nbsp;', '').replace(' ', '').replace('\xa0', ''))
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


def clean_number(value):
    """
    Очищает число от форматирования и преобразует в int

    """
    if isinstance(value, str):
        # Удаляем все нецифровые символы кроме минуса
        cleaned = ''.join(c for c in value if c.isdigit() or c == '-')
        return int(cleaned) if cleaned else 0
    return value


def prepare_data_for_excel(data):
    """
    Подготавливает данные для записи в Excel

    """
    excel_data = []

    for item in data:
        # Преобразуем дату в формат с временем
        period_number = f"{item['date']} 00:00:00"

        # Очищаем числовые значения
        cleaned_item = {
            'period_number': period_number,
            'y': clean_number(item['y']),
            'x_1': clean_number(item['x1']),
            'x_2': clean_number(item['x2']),
            'x_3': clean_number(item['x3']),
            'x_4': clean_number(item['x4']),
            'x_5': clean_number(item['x5']),
            'x_6': clean_number(item['x6']),
            'x_7': clean_number(item['x7']),
            'x_8': clean_number(item['x8']),
            'x_9': clean_number(item['x9'])
        }
        excel_data.append(cleaned_item)

    return excel_data


data =[]
for link in filtered_href:
    url_101 = url + link
    response_101 = session.get(url_101, headers=headers)
    soup_101 = BeautifulSoup(response_101.text, "html.parser")

# х4 — итог баланса банка, млн руб.;

    row_x4 = soup_101.find('tr', class_='italic')
    if row_x4:
        # Все ячейки с классом right
        cells = row_x4.find_all('td', class_='right')
        # Последняя ячейка (индекс -1)
        last_cell = cells[-1] if cells else None
        x4 = last_cell.text.replace(' ', '').replace('\xa0', '').replace(' ', '')
    else:
        x4 = 0

    # х8 — кредитный портфель (45.0 + 45.2);
    # х9 — Просроченная задолженность (458 + 459);

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
    print(data)

# х5 — процентные расходы;
# x6 — процентные доходы;

date_from_data = ''
for el in data:
    date_from_data = el['date']
    url_102 = url + '/banking_sector/credit/coinfo/f102?regnum=354&dt=' + date_from_data
    response = session.get(url_102, headers=headers)
    soup_102 = BeautifulSoup(response.text, "html.parser")
    el['x5'] = search_for_102(soup_102, date_from_data, 'Раздел 1. Процентные расходы', 'Итого по разделу 1', "Раздел 1. Процентные расходы")
    el['x6'] = search_for_102(soup_102, date_from_data, 'Раздел 1. Процентные доходы', 'Итого по разделу 1', "Раздел 1. Процентные доходы")
    if date_from_data >= '2016-12-01':
        el['y'] = search_for_102_y(soup_102, '1. Финансовый результат после налогообложения')
    elif date_from_data >= '2009-01-01':
        el['y'] = search_for_102_y(soup_102, 'Раздел 1. Финансовый результат после налогообложения')
    else:
        el['y'] = search_for_102_y(soup_102, 'Итого результат по отчету')
    print(data)

# Подготавливаем данные
excel_ready_data = prepare_data_for_excel(data)

# Создаем DataFrame
df = pd.DataFrame(excel_ready_data)
column_order = ['period_number', 'y', 'x_1', 'x_2', 'x_3', 'x_4', 'x_5', 'x_6', 'x_7', 'x_8', 'x_9']
df = df[column_order]

# Записываем в Excel файл
with pd.ExcelWriter('bank.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Лист1', index=False)

    # Получаем workbook и worksheet для дополнительного форматирования
    workbook = writer.book
    worksheet = writer.sheets['Лист1']

    # Автоподбор ширины колонок
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column_letter].width = adjusted_width

print("Данные успешно записаны в bank.xlsx")


