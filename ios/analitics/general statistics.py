from operator import index
from typing import final

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from fontTools.subset import subset
from sympy.abc import lamda

df_currency = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "currency.csv"),  index_col='date')


def get_currency_from_the_central_banks_API():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"

    date_req1 = pd.to_datetime("2024-11-01")
    date_req2 = pd.to_datetime("2003-01-01")
    headers = ["date", "BYR", "USD", "EUR", "KZT", "UAH", "AZN", "KGS", "UZS", "GEL"]
    result = []

    while date_req2 <= date_req1:
        current_date = date_req2.strftime("%d/%m/%Y")

        parameters = {
            "date_req": current_date
        }

        response = requests.get(url, params=parameters)
        root = ET.fromstring(response.content)

        result_date = date_req2.strftime("%Y-%m")

        row = {
            "date": result_date
        }

        for valute in root.findall(".//Valute"):
            char_code = valute.find("CharCode").text
            vunit_rate = float(valute.find("VunitRate").text.replace(",", "."))

            if char_code in headers:
                row[char_code] = vunit_rate

        result.append(row)
        date_req2 += pd.DateOffset(months=1)

    currency = pd.DataFrame(result)
    currency = currency[headers]
    currency.to_csv(path_or_buf="currency.csv", index=False, encoding="utf-8")


def load_currency_dict(file_path):
    """Загрузка данных о курсах валют в виде словаря."""
    return pd.read_csv(file_path).set_index("date").to_dict("index")


def process_chunk(chunk, currency_dict):
    """Обработка части данных (chunk) с учетом курсов валют."""
    # Предобработка данных
    chunk["salary_from"] = pd.to_numeric(chunk["salary_from"], errors="coerce")
    chunk["salary_to"] = pd.to_numeric(chunk["salary_to"], errors="coerce")
    chunk["published_at"] = pd.to_datetime(chunk["published_at"], errors="coerce")

    # Вычисление средней зарплаты
    chunk["average_salary"] = chunk[["salary_from", "salary_to"]].mean(axis=1)

    # Преобразование даты в формат YYYY-MM для маппинга курсов валют
    chunk["date"] = pd.to_datetime(chunk["published_at"], utc=True).dt.strftime("%Y-%m")
    chunk["exchange_rate"] = chunk.apply(
        lambda row: currency_dict.get(row["date"], {}).get(row["salary_currency"],
                                                           1 if row["salary_currency"] == "RUR" else None),
        axis=1,
    )

    # Удаление строк с отсутствующими курсами или датами
    chunk.dropna(subset=["average_salary", "exchange_rate"], inplace=True)

    # Перевод зарплаты в рубли
    chunk["salary"] = chunk["average_salary"] * chunk["exchange_rate"]

    # Фильтрация по зарплате
    chunk = chunk[(chunk["salary"] <= 10_000_000)]

    return chunk


def get_preparing_vacancies():
    # Пути к файлам
    vacancies_file = os.path.join(os.path.dirname(__file__), "data", "vacancies_2024.csv")
    currency_file = os.path.join(os.path.dirname(__file__), "data", "currency.csv")

    # Загрузка курсов валют
    currency_dict = load_currency_dict(currency_file)

    # Результирующий DataFrame
    results = []

    # Обработка файла частями
    chunk_size = 100_000  # Размер чанка
    for chunk in pd.read_csv(vacancies_file, chunksize=chunk_size, low_memory=False):
        processed_chunk = process_chunk(chunk, currency_dict)
        results.append(processed_chunk)

    # Объединение результатов
    final_data = pd.concat(results, ignore_index=True)

    final_data.to_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")


def get_salary_level_by_years():
    final_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")
    # Вычисление средней зарплаты по годам
    final_data["year"] = pd.to_datetime(final_data["published_at"], utc=True).dt.year
    salary_level_by_years = (
        final_data.groupby("year")["salary"]
        .mean()
        .round()
        .astype(int)
    )

    # Сохранение результата
    salary_level_by_years.to_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_by_years.csv"), encoding="utf-8")


def get_count_vacancies_by_years():
    final_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")

    final_data["year"] = pd.to_datetime(final_data["published_at"], utc=True).dt.year
    count_vacancies_by_years = (
        final_data.groupby("year")
        .size()
        .reset_index(name="count")
    )

    count_vacancies_by_years.to_csv(os.path.join(os.path.dirname(__file__), "data", "count_vanancies_by_years.csv"), encoding="utf-8")


def get_salary_level_by_cities():
    final_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")

    lev_vacancies = len(final_data)

    salary_level_by_cities =(
        final_data.groupby("area_name")
        .agg(average_by_cities=("salary", "mean"),
        count=("name", "count"))
        .apply(np.round)
        .assign(perc=lambda x: x["count"] / lev_vacancies)
        .sort_values("average_by_cities", ascending=False)
        .query("perc >= 0.01")
        .reset_index()[["average_by_cities", "area_name"]]
    )

    salary_level_by_cities.to_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_by_cities.csv"), encoding="utf-8")


def get_fraction_vacancies_by_cities():
    final_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")

    len_vacancies = len(final_data)

    fraction_vacancies = (
        final_data.groupby("area_name")
        .agg(count=("name", "count"))
        .assign(perc=lambda x: x["count"] / len_vacancies)
        .sort_values("count", ascending=False)
        .query("perc >= 0.01")
        .reset_index()[["count", "area_name"]]
    )

    fraction_vacancies.to_csv(os.path.join(os.path.dirname(__file__), "data", "fraction_vacancies.csv"), encoding="utf-8")


def get_top20_skills_by_years():
    final_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")
    final_data["year"] = pd.to_datetime(final_data["published_at"], utc=True).dt.year

    preparing_skills =(
        final_data.dropna(subset=["key_skills"])
        .assign(key_skills=final_data["key_skills"].str.split(r",|\n|\s{2,}"))
        .explode("key_skills")
    )

    preparing_skills["key_skills"] = preparing_skills["key_skills"].str.strip()
    skills_expanded = preparing_skills[preparing_skills["key_skills"] != ""]

    top20_skills_by_years = (
        skills_expanded.groupby(["year", "key_skills"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "key_skills"], ascending=[True, False])
        .groupby("year")
        .head(20)
    )

    top20_skills_by_years["key_skills"] = top20_skills_by_years["key_skills"].str.strip().str.replace(r"[^\w\s,()\-.:]", "", regex=True)

    top20_skills_by_years.to_csv(os.path.join(os.path.dirname(__file__), "data", "top20_skills_by_years.csv"))


def get_image_dynamics_salary_level_by_years():
    salary_level_by_years = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_by_years.csv"))
    fig, sub = plt.subplots(2, 2, figsize=(12, 8))

    x = np.arange(len(salary_level_by_years.index))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.plot(salary_level_by_years["year"], salary_level_by_years["salary"], marker="o", linestyle="-", color="b")
    plt.title('Динамика зарплат по годам')
    plt.xlabel('Год')
    plt.ylabel('Зарплата, руб')
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "general", "dynamics_salary_level_by_years.png"), format="png", dpi=300)
    plt.close()


def get_table_dynamics_salary_by_years():
    salary_level_by_years = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_by_years.csv"), encoding="utf-8")

    salary_level_by_years.columns = ["Год", "Средняя зарплата"]

    table = salary_level_by_years.to_html()

    with open(os.path.join(os.path.dirname(__file__), "static", "general", "table_salary_level_by_years.html"), "w", encoding="utf-8") as file:
        file.write(table)


def get_image_dynamics_count_vacancies_by_years():
    count_vanancies_by_years = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "count_vanancies_by_years.csv"), encoding="utf-8")
    fig, sub = plt.subplots(2, 2, figsize=(12, 8))

    x = np.arange(len(count_vanancies_by_years.index))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.plot(count_vanancies_by_years["year"], count_vanancies_by_years["count"], marker="o", linestyle="-", color="b")
    plt.title('Динамика количества вакансий по годам')
    plt.xlabel('Год')
    plt.ylabel('Количество вакансий')
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "general", "dynamics_count_vacancies_by_years.png"), format="png",
                dpi=300)
    plt.close()


def get_table_dynamics_count_vacancies_by_years():
    count_vanancies_by_years = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "count_vanancies_by_years.csv"), encoding="utf-8")
    count_vanancies_by_years.drop(count_vanancies_by_years.columns[0], axis=1, inplace=True)

    count_vanancies_by_years.columns = ["Год", "Количество вакансий"]

    table = count_vanancies_by_years.to_html()

    with open(os.path.join(os.path.dirname(__file__), "static", "general", "table_count_vacancies_by_years.html"), "w", encoding="utf-8") as file:
        file.write(table)


def get_dynamics_salary_level_by_cities():
    salary_level_by_cities = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_by_cities"))

    plt.figure(figsize=(12, 6))
    plt.barh(salary_level_by_cities['area_name'], salary_level_by_cities['average_by_cities'], color='skyblue')

    plt.title('Уровень зарплат по городам')
    plt.xlabel('Зарплата, руб')
    plt.ylabel('Город')
    plt.grid(True, axis='x')

    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "general", "salary_level_by_cities.png"),
                format="png",
                dpi=350)
    plt.close()


def get_table_dynamics_salary_level_by_cities():
    salary_level_by_cities = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "salary_level_by_cities"), encoding="utf-8")
    salary_level_by_cities.drop(salary_level_by_cities.columns[0], axis=1, inplace=True)

    salary_level_by_cities.columns = ["Средняя зарплата", "Город"]

    table = salary_level_by_cities.to_html()

    with open(os.path.join(os.path.dirname(__file__), "static", "general", "table_salary_level_by_cities.html"), "w", encoding="utf-8") as file:
        file.write(table)


def get_image_fraction_vacancies_by_cities():
    fraction_vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "fraction_vacancies.csv"), encoding="utf-8")

    plt.figure(figsize=(10, 10))
    fraction_vacancies.set_index('area_name')['count'].plot(kind='pie', autopct='%1.1f%%', colors=plt.cm.Paired.colors)

    plt.title('Доля вакансий по городам')
    plt.ylabel('')
    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "general", "fraction_vacancies_by_cities.png"),
                format="png",
                dpi=300)
    plt.close()


def get_table_fraction_vacancies_by_years():
    fraction_vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "fraction_vacancies.csv"), encoding="utf-8")

    fraction_vacancies.drop(fraction_vacancies.columns[0], axis=1, inplace=True)

    fraction_vacancies.columns = ["Количество вакансий", "Город"]

    table = fraction_vacancies.to_html()

    with open(os.path.join(os.path.dirname(__file__), "static", "general", "table_fraction_vacancies_by_cities.html"), "w", encoding="utf-8") as file:
        file.write(table)


if __name__ == '__main__':
    get_dynamics_salary_level_by_cities()