import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from fontTools.subset import subset
from sympy.abc import lamda


def get_salary_level_ios_developer_by_cities():
    vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "filtering_vacancies.csv"), encoding="utf-8")

    lev_vacancies = len(vacancies)

    salary_level_ios_developer_by_cities = (
        vacancies.groupby("area_name")
        .agg(average_by_cities=("salary", "mean"),
             count=("name", "count"))
        .apply(np.round)
        .assign(perc=lambda x: x["count"] / lev_vacancies)
        .sort_values("average_by_cities", ascending=False)
        .query("perc >= 0.01")
        .reset_index()[["average_by_cities", "area_name"]]
    )

    salary_level_ios_developer_by_cities.to_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_cities.csv"), encoding="utf-8")


def get_count_ios_developer_by_cities():
    vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "filtering_vacancies.csv"),
                            encoding="utf-8")

    len_vacancies = len(vacancies)

    count_ios_developer_by_cities = (
        vacancies.groupby("area_name")
        .agg(count=("name", "count"))
        .assign(perc=lambda x: x["count"] / len_vacancies)
        .sort_values("count", ascending=False)
        .query("perc >= 0.01")
        .reset_index()[["count", "area_name"]]
    )

    count_ios_developer_by_cities.to_csv(
        os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_cities.csv"), encoding="utf-8")


def get_image_salary_level_ios_developer_by_cities():
    salary_level_ios_developer_by_cities = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_cities.csv"))

    plt.figure(figsize=(12, 6))
    plt.barh(salary_level_ios_developer_by_cities['area_name'], salary_level_ios_developer_by_cities['average_by_cities'], color='skyblue')

    plt.title('Уровень зарплат по городам ios-разработчика')
    plt.xlabel('Зарплата, руб')
    plt.ylabel('Город')
    plt.grid(True, axis='x')

    plt.savefig(os.path.join(os.path.dirname(__file__), "salary_level_ios_developer_by_cities.png"),
                format="png",
                dpi=350)
    plt.close()


def get_table_salary_level_ios_developer_by_cities():
    salary_level_ios_developer_by_cities = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_cities.csv"), encoding="utf-8")
    salary_level_ios_developer_by_cities.drop(salary_level_ios_developer_by_cities.columns[0], axis=1, inplace=True)

    salary_level_ios_developer_by_cities.columns = ["Средняя зарплата", "Город"]

    table = salary_level_ios_developer_by_cities.to_html()

    with open(os.path.join(os.path.dirname(__file__), "salary_level_ios_developer_by_cities.html"), "w",
              encoding="utf-8") as file:
        file.write(table)


def get_image_count_ios_developer_by_cities():
    count_ios_developer_by_cities = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_cities.csv"),
                                     encoding="utf-8")

    plt.figure(figsize=(10, 10))
    count_ios_developer_by_cities.set_index('area_name')['count'].plot(kind='pie', autopct='%1.1f%%', colors=plt.cm.Paired.colors)

    plt.title('Доля вакансий по городам ios-разработчика')
    plt.ylabel('')
    plt.savefig(os.path.join(os.path.dirname(__file__), "table_count_ios_developer_by_cities.png"),
                format="png",
                dpi=300)
    plt.close()


def get_table_count_ios_developer_by_cities():
    count_ios_developer_by_cities = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_cities.csv"),
                                     encoding="utf-8")

    count_ios_developer_by_cities.drop(count_ios_developer_by_cities.columns[0], axis=1, inplace=True)

    count_ios_developer_by_cities.columns = ["Количество вакансий", "Город"]

    table = count_ios_developer_by_cities.to_html()

    with open(os.path.join(os.path.dirname(__file__), "table_count_ios_developer_by_cities.html"),
              "w", encoding="utf-8") as file:
        file.write(table)


if __name__ == '__main__':
    get_table_count_ios_developer_by_cities()