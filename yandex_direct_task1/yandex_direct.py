# библиотеки для сбора данных
import requests
from requests.exceptions import ConnectionError
from time import sleep
import json
# библиотеки для вывода отчета
import pandas as pd
from pandas import DataFrame

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)

# Метод для корректной обработки строк в кодировке UTF-8 как в Python 3, так и в Python 2
import sys

if sys.version_info < (3,):
    def u(x):
        try:
            return x.encode("utf8")
        except UnicodeDecodeError:
            return x
else:
    def u(x):
        if type(x) == type(b''):
            return x.decode('utf8')
        else:
            return x

# --- Входные данные ---
# Адрес сервиса Reports для отправки JSON-запросов (регистрозависимый)
ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'

# OAuth-токен пользователя, от имени которого будут выполняться запросы

token = ''  # ------------------------------------Ввести токен
clientLogin = ''  # ------------------------------Ввести логин

# --- Подготовка запроса ---
# Создание HTTP-заголовков запроса
headers = {
    # OAuth-токен. Использование слова Bearer обязательно
    "Authorization": "Bearer " + token,
    # Логин клиента рекламного агентства
    "Client-Login": clientLogin,
    # Язык ответных сообщений
    "Accept-Language": "ru",
    # Режим формирования отчета
    "processingMode": "auto"
    # Формат денежных значений в отчете
    # "returnMoneyInMicros": "false",
    # Не выводить в отчете строку с названием отчета и диапазоном дат
    # "skipReportHeader": "true",
    # Не выводить в отчете строку с названиями полей
    # "skipColumnHeader": "true",
    # Не выводить в отчете строку с количеством строк статистики
    # "skipReportSummary": "true"
}

# Создание тела запроса
body = {
    "params": {
        "SelectionCriteria": {
            "Filter": [
                {
                    "Field": "Clicks",
                    "Operator": "GREATER_THAN",
                    "Values": [
                        "0"
                    ]
                },

            ]
        },
        # поля которые будут отображаться в отчете
        "FieldNames": [
            "CampaignName",
            "Impressions",
            "Clicks",
            "Ctr",
            "Cost",
            "AvgCpc",
            "BounceRate",
            "AvgPageviews",
            "ConversionRate",
            "CostPerConversion",
            "Conversions"
        ],
        "ReportName": u("REPORT"),
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "DateRangeType": "LAST_5_DAYS",  # здесь выбрать диапазон
        "Format": "TSV",
        "IncludeVAT": "NO",
        "IncludeDiscount": "NO"
    }
}

# Кодирование тела запроса в JSON
body = json.dumps(body, indent=4)

# --- Запуск цикла для выполнения запросов ---
# Если получен HTTP-код 200, то выводится содержание отчета
# Если получен HTTP-код 201 или 202, выполняются повторные запросы
while True:
    try:
        req = requests.post(ReportsURL, body, headers=headers)
        req.encoding = 'utf-8'  # Принудительная обработка ответа в кодировке UTF-8
        if req.status_code == 400:
            print("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
            print("RequestId: {}".format(req.headers.get("RequestId", False)))
            print("JSON-код запроса: {}".format(u(body)))
            print("JSON-код ответа сервера: \n{}".format(u(req.json())))
            break
        elif req.status_code == 200:
            format(u(req.text))
            break
        elif req.status_code == 201:
            print("Отчет успешно поставлен в очередь в режиме офлайн")
            retryIn = int(req.headers.get("retryIn", 60))
            print("Повторная отправка запроса через {} секунд".format(retryIn))
            print("RequestId: {}".format(req.headers.get("RequestId", False)))
            sleep(retryIn)
        elif req.status_code == 202:
            print("Отчет формируется в режиме офлайн")
            retryIn = int(req.headers.get("retryIn", 60))
            print("Повторная отправка запроса через {} секунд".format(retryIn))
            print("RequestId:  {}".format(req.headers.get("RequestId", False)))
            sleep(retryIn)
        elif req.status_code == 500:
            print("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее")
            print("RequestId: {}".format(req.headers.get("RequestId", False)))
            print("JSON-код ответа сервера: \n{}".format(u(req.json())))
            break
        elif req.status_code == 502:
            print("Время формирования отчета превысило серверное ограничение.")
            print(
                "Пожалуйста, попробуйте изменить параметры запроса - уменьшить период и количество запрашиваемых данных.")
            print("JSON-код запроса: {}".format(body))
            print("RequestId: {}".format(req.headers.get("RequestId", False)))
            print("JSON-код ответа сервера: \n{}".format(u(req.json())))
            break
        else:
            print("Произошла непредвиденная ошибка")
            print("RequestId:  {}".format(req.headers.get("RequestId", False)))
            print("JSON-код запроса: {}".format(body))
            print("JSON-код ответа сервера: \n{}".format(u(req.json())))
            break

    # Обработка ошибки, если не удалось соединиться с сервером API Директа
    except ConnectionError:
        # В данном случае мы рекомендуем повторить запрос позднее
        print("Произошла ошибка соединения с сервером API")
        # Принудительный выход из цикла
        break

    # Если возникла какая-либо другая ошибка
    except:
        # В данном случае мы рекомендуем проанализировать действия приложения
        print("Произошла непредвиденная ошибка")
        # Принудительный выход из цикла
        break

# формируем вывод данных
file = open("data.csv", "w")
file.write(req.text)
file.close()
result_frame = pd.read_csv("data.csv", header=1, sep='	', index_col=0, )

print(result_frame)
