import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install bs4
from fake_useragent import UserAgent  # pip install fake_useragent
from pprint import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta

ua = UserAgent()
url = "https://cbr.ru"
headers = {"User-Agent": ua.chrome}
session = requests.session()  # аналогия с открытой вкладкой

# https://cbr.ru/banking_sector/credit/coinfo/f102?regnum=354&dt=2025-08-01
url_102 = url + '/banking_sector/credit/coinfo/f102?regnum=354&'
params = {"dt": "2008-06-01"}

response = session.get(url_102, headers=headers, params=params)
soup_102 = BeautifulSoup(response.text, "html.parser")
print()



# for item in iterable:
#     if flag:
#         # это следующий после нужного элемента
#         обрабатываем следующий элемент
#         found = False  # сбрасываем, если нужно только один следующий
#     if условие на нужный элемент:
#         flag = True

flag = False
if soup_102.find_all('tr'):
    for row in soup_102.find_all('tr'):
        cell = row.find('td')
        if cell:
            cell_text = cell.getText().strip()
            if cell_text == "Раздел 1. Процентные расходы":
                flag = True


            # Если в этой строке мы нашли нужный account, то сохраняем и выходим
            if account in cell_text:
                target_row = row
# while params['dt'] != '2025-10-01':
#     response = session.get(url_102, headers=headers, params=params)
#     soup_102 = BeautifulSoup(response.text, "html.parser")
#     posts = soup.find_all('div', {'class': 'post-item event'})
#     if not posts:
#         break
#     for post in posts:
#         post_info = {}
#         name_info = post.find('a', {"class": 'post-item__title h3 search_text'})
#         post_info['name'] = name_info.getText()
#         post_info['url'] = url + name_info.get('href')
#
#         add_info = post.find('div', {'class': 'text-muted'}).findChildren('span')
#         post_info['views'] = int(add_info[0].getText())
#         post_info['comments'] = int(add_info[1].getText())
#         all_posts.append(post_info)
#     print(f'Обработана {params["page"]} страница')
#     params['page'] += 1
# pprint(all_posts)
#
# d = '2025-08-01'
#
# # Преобразуем строку в объект datetime
# current_date = datetime.strptime(d, '%Y-%m-%d')
#
# # Увеличиваем на 1 месяц
# next_month = current_date + relativedelta(months=1)
#
# # Преобразуем обратно в строку
# next_month_str = next_month.strftime('%Y-%m-%d')
# print(f"Исходная дата: {d}")
# print("Дата +1 месяц" + str(next_month_str))


# list_1 = ['2', '3', '4']
# summ_list_1 = 0
# for i in list_1:
#     summ_list_1 += int(i)
#
# print(summ_list_1)
#
# list_1 = ['2', '3', '4']
# summ_list_1 = sum(map(int, list_1))
# print(summ_list_1)  # 9
#
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
#
# d = '2025-08-01'
#
# # Преобразуем строку в объект datetime
# current_date = datetime.strptime(d, '%Y-%m-%d')
#
# # Увеличиваем на 1 месяц
# next_month = current_date + relativedelta(months=1)
#
# # Преобразуем обратно в строку
# next_month_str = next_month.strftime('%Y-%m-%d')
# print(f"Исходная дата: {d}")
# print("Дата +1 месяц" + str(next_month_str))