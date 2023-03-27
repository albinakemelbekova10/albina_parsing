# импортируем библиотеки
import random
from time import sleep
import requests
from bs4 import BeautifulSoup
import json
import csv

# ссылка на сайт
# url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

# это наши данные, чтобы доказать что я человек
headers = {
    "accept": "*/*",
    "user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69",
}

# отправляем запрос на сайт, видишь здесь переменная url, ну и типа подумай что мы отправляем запрос на сайт
# и в переменную req мы также добавляем наши данные
# req = requests.get(url, headers=headers)

# мы сначала создаем, открываем и пишем html код на главной странице
# with open("1/index.html", "w", encoding="utf-8") as file:
#     file.write(src)

# а вот здесь читаем код, чтобы прочитать
with open("1/index.html", "r", encoding="utf-8") as file:
    src = file.read()

# по факту, мы говорим библиотеке BeautifulSoup что типа вот переменная src, (принимай его значения)
soup = BeautifulSoup(src, "lxml")
# мы ищем все ссылки у продуктов с классом mzr-tc-group-item-href
all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")

# это json объект, в который мы будем сохранять данные
all_categories_dict = {}

# цикл, в котором мы парсим все ссылки на подробную информацию
for item in all_products_hrefs:
    item_text = item.text
    item_href = "https://health-diet.ru" + item.get("href")

    # здесь мы записываем это все в json файл
    all_categories_dict[item_text] = item_href

# мы сохраянем данные в словарь (или json файл)
with open("1/all_categories_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

# загружаем данные в переменную all_categories
with open("1/all_categories_dict.json", encoding="utf-8") as file:
    all_categories = json.load(file)

# в переменную iteration_count мы назначаем длину всех категорий
# и это все, для того чтобы в терминал у нас показывался процесс нашего парсинга. Типо как загрузка
iteration_count = int(len(all_categories)) - 1  # по факту здесь 55
count = 0
print(f"Всего итераций: {iteration_count}")

# заменяем [",", " ", "-", "'"]  на "_" (нижнее подчеркивание)
for category_name, category_href in all_categories.items():

    rep = [",", " ", "-", "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")

    # снова отправляем запрос
    req = requests.get(url=category_href, headers=headers)
    src = req.text

    # парсим html код каждого продукта
    with open(f"1/data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    # открываем, читаем
    with open(f"1/data/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()

    # снов скармливаем
    soup = BeautifulSoup(src, "lxml")

    # проверка страницы на наличие таблицы с продуктами
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # собираем заголовки таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f"1/data/{count}_{category_name}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow((product, calories, proteins, fats, carbohydrates))

    # собираем данные продуктов
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []
    for item in products_data:
        product_tds = item.find_all("td")

        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates,
            }
        )

        with open(f"1/data/{count}_{category_name}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow((title, calories, proteins, fats, carbohydrates))
    with open(f"1/data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"# Итерация {count}. {category_name} записан...")
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print("Работа завершена")
        break

    print(f"Осталось итераций: {iteration_count}")
    sleep(random.randrange(2, 4))
