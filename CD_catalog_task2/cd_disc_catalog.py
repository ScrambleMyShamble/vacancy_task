import requests
import xml.etree.ElementTree as ET


# Задание в вакансии

# №1 Считать стоимость всех дисков в каталоге. all_prices[]
# №2 Какой год для дисков в каталоге является последним. years[]
def parse_xml(data) -> dict:
    all_prices = []
    years = []
    # проходимся циклом в корневом элементе вытаскивая по имени нужные атрибуты
    for item in root:
        price = item.find('PRICE').text
        year = item.find('YEAR').text
        # добавляем в результирующий набор
        all_prices.append(price)
        years.append(int(year))
    # не очень понял что значит 'последним', последний в спике или последний по дате выхода(самый свежий)
    result_dict = {'prices': all_prices, 'last_year': [years[-1], max(years)]}
    # возвращаем словарь с двумя списками, ценами и годами
    return result_dict


# №3 Компания «Polydor» сменила своё название на «Poly», измените название этой компании у всех CD
# на актуальное в XML каталоге и сохраните новый XML файл
def set_old_xml_file(data):
    for item in root:
        # находим в цикле нужную компанию и меняем название
        if item.find('COMPANY').text == 'Polydor':
            item.find('COMPANY').text = 'Poly'
    # создаём новый xml файл с изменёнными данными
    tree.write('new.xml')


# через requests получаем данные по ссылке
url = 'https://www.w3schools.com/xml/cd_catalog.xml'
r_get = requests.get(url)
# записываем полученный ответ в виде текста в xml файл, дальше работаем уже с xml файлом
with open('../old_data.xml', 'w') as d:
    d.write(r_get.text)

# скармливаем ET xml файл
tree = ET.parse('../old_data.xml')
# встроенным методом получаем корневой элемент, по нему пройдёмся циклом и вытащим нужные атрибуты
root = tree.getroot()
print(set_old_xml_file(root))
