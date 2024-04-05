import pandas as pd
import numpy as np
from typing_extensions import OrderedDict
from itertools import groupby

# Чтение данных
article = pd.read_excel('data/art.xlsx')
df_1 = pd.read_excel('data/sales_1.xlsx')
df_2 = pd.read_excel('data/sales_2.xlsx')

# Удаляем первую строку
df_11 = df_1.iloc[1:]
df_22 = df_2.iloc[1:]

df = pd.concat([df_11, df_22]) # Объединение строк из разных объектов данных в один объект данных
uniq_df = df.drop_duplicates() # Удаление дубликатов

print('Оставляем позиции, которые продавались больше 2 раз')
article = article[article['quantity_of_sales'] > 2] # Оставляем позиции, которые продавались больше 2 раз
article = article.reset_index(drop=True) # Сбрасываем индекс
article.index = article.index + 1 # Начинаем индексацию с 1
article_copy = article[['code2']].copy()  # Создаем копию DataFrame'а article с одним столбцом 'code2'
print('Группируем данные')
grouped_uniq_df = uniq_df.groupby('code2')['sales_document'].apply(list).reset_index()  # Группируем данные в uniq_df по 'code2' и объединяем значения 'sales_document' в списки
merged_data = pd.merge(article_copy, grouped_uniq_df, on='code2', how='left')  # Объединяем данные с помощью merge
merged_data = merged_data.explode('sales_document')  # Раскрываем список документов продаж в отдельные строки
final_merged_data = pd.merge(merged_data, uniq_df, on=['sales_document'], how='left')  # Объединяем раскрытые данные с таблицей uniq_df, чтобы получить соответствующие коды товаров
final_merged_data = final_merged_data[final_merged_data['code2_x'] != final_merged_data['code2_y']] # Фильтруем данные, исключая строки, где code2_x равен code2_y
pivot_table = final_merged_data.groupby(['code2_x', 'code2_y']).size().reset_index(name='Количество_code2_y') # Группируем данные по 'code2_x' и 'code2_y', подсчитываем количество
pivot_table = pivot_table.sort_values(by=['code2_x', 'Количество_code2_y'], ascending=[True, False]) # Сортируем по 'code2_x' и 'Количество_code2_y'
print('Формируем топ 20')
pivot_table = pivot_table.groupby('code2_x').head(20)  # Получаем только первые 20 позиций 'code2_y' для каждого 'code2_x'
pivot_table = pd.merge(pivot_table, article[['code2', 'quantity_of_sales']], left_on='code2_x', right_on='code2', how='left')  # Объединяем pivot_table с article, чтобы получить 'quantity_of_sales' для соответствующих 'code2_x'
pivot_table['Отношение'] = pivot_table['Количество_code2_y'] / pivot_table['quantity_of_sales']  # Добавляем столбец с результатом деления 'Количество_code2_y' на 'quantity_of_sales'

# Создаем 2 списка для проверки основного условия выбора, и дополнительного
main_list = []
additional_list = []
print('Итерация по списку, для проверки условий')
#Итерация по каждой позиции
for index, row in pivot_table.iterrows():
  main_code = row['code2_x']
  additional_code = row['code2_y']
  count_additional_code = row['Количество_code2_y']
  percentage_presence = row['Отношение']
  #Проверка основного условия и добавления в первый список
  if count_additional_code > 2 and percentage_presence >= 0.15:
    main_list.append({
        'Основной_code2' : main_code,
        'Сопутствующий_code2' : additional_code
    })
    print('/')
    #Проверка второго условия и добавление во второй список
  elif count_additional_code > 10 and (percentage_presence > 0.05 and percentage_presence < 0.15):
        additional_list.append({
        'Основной_code2_2' : main_code,
        'Сопутствующий_code2_2' : additional_code
    })
        print('.')
        
main_list_sorted = sorted(main_list, key=lambda x: x['Основной_code2'])  # Сортируем список по значению 'Основной_code2'

# Проверяем, если нет записей в additional_list по второму алгоритму, то сохраняем данные с первого алгоритма
if len(additional_list) == 0:
    main_list_sorted = pd.DataFrame(main_list_sorted)
    main_list_sorted.to_excel("main_list.xlsx")
    # если в additional_list еанные имеются, то добавляем к первому списку, где сопутствующих товаров меньше 3
else:
    print('Фильтруем словарь, оставляем только те позиции, у которых количество меньше 3')
    grouped_main_list = groupby(main_list_sorted, key=lambda x: x['Основной_code2'])  # Группируем отсортированный список по значению 'Основной_code2'
# Создаем словарь, в котором ключами будут значения 'Основной_code2', а значениями - количество элементов в группе
    group_counts = {key: len(list(group)) for key, group in grouped_main_list} 
    filtered_group_counts = {key: value for key, value in group_counts.items() if value < 3} # Фильтруем словарь, оставляем только те позиции, у которых количество меньше 3       
# Создаем DataFrame из ключей словаря filtered_group_counts с указанием типа данных столбца
    filtered_keys_df = pd.DataFrame({'Основной_code2': list(filtered_group_counts.keys())}, dtype=int)
 # Преобразуем список additional_list в DataFrame
    additional_df = pd.DataFrame(additional_list)
# Группируем данные в additional_df по 'Основной_code2_2' и объединяем значения 'Сопутствующий_code2_2' в списки
    grouped_additional_list = additional_df.groupby('Основной_code2_2')['Сопутствующий_code2_2'].apply(list).reset_index() 
    print('Объединяем список позиций, у которых было меньше 3х аналогов с дополнительным условием отбора')
# Объединяем список позиций, у которых было меньше 3х аналогов с дополнительным условием отбора
    merged_data_main_additional = pd.merge(filtered_keys_df, grouped_additional_list, left_on='Основной_code2', right_on='Основной_code2_2', how='left')  
    merged_data_main_additional = merged_data_main_additional.explode('Сопутствующий_code2_2')  # Раскрываем список  в отдельные строки
# Удаляем столбец "Основной_code2_2"
    merged_data_main_additional.drop(columns=['Основной_code2_2'], inplace=True)

# Переименовываем столбец "Сопутствующий_code2_2" в "Сопутствующий_code2"
    merged_data_main_additional.rename(columns={'Сопутствующий_code2_2': 'Сопутствующий_code2'}, inplace=True)
# Удаляем строки, где значения в ячейках столбца 'Сопутствующий_code2' пусты
    merged_data_main_additional.dropna(subset=['Сопутствующий_code2'], inplace=True)

# Преобразуем списки main_list и merged_data_main_additional в DataFrame
    main_list_df = pd.DataFrame(main_list)
    merged_data_main_additional_df = pd.DataFrame(merged_data_main_additional)

# Объединяем DataFrame main_list_df и merged_data_main_additional_df
    final_main_list = pd.concat([main_list_df, merged_data_main_additional_df], ignore_index=True)
    final_main_list.to_excel("final_main_list.xlsx")
