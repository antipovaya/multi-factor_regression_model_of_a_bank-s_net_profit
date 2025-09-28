list_1 = ['2', '3', '4']
summ_list_1 = 0
for i in list_1:
    summ_list_1 += int(i)

print(summ_list_1)

list_1 = ['2', '3', '4']
summ_list_1 = sum(map(int, list_1))
print(summ_list_1)  # 9