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


def filter_vacancies(name):
    vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "final_vacancies.csv"), encoding="utf-8")
    filtering_vacancies = vacancies[vacancies["name"].str.contains(rf"\b{name}\b", case=False, na=False)]

    filtering_vacancies.to_csv(os.path.join(os.path.dirname(__file__), "data", "filtering_vacancies.csv"), encoding="utf-8")


def get_salary_level_ios_developer_by_years():
    vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "filtering_vacancies.csv"), encoding="utf-8")

    vacancies["year"] = pd.to_datetime(vacancies["published_at"], utc=True).dt.year
    salary_level_ios_developer_by_years = (
        vacancies.groupby("year")["salary"]
        .mean()
        .round()
        .astype(int)
    )

    salary_level_ios_developer_by_years.to_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_years.csv"), encoding="utf-8")


def get_count_ios_developer_by_years():
    vacancies = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "filtering_vacancies.csv"), encoding="utf-8")

    vacancies["year"] = pd.to_datetime(vacancies["published_at"], utc=True).dt.year
    count_ios_developer_by_years = (
        vacancies.groupby("year")
        .size()
        .reset_index(name="count")
    )

    count_ios_developer_by_years.to_csv(os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_years.csv"), encoding="utf-8")


def get_image_dynamics_salary_level_ios_developer_by_years():
    salary_level_ios_developer_by_years = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_years.csv"), encoding="utf-8")
    fig, sub = plt.subplots(2, 2, figsize=(12, 8))

    x = np.arange(len(salary_level_ios_developer_by_years.index))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.plot(salary_level_ios_developer_by_years["year"], salary_level_ios_developer_by_years["salary"], marker="o", linestyle="-", color="b")
    plt.title('Динамика зарплат по годам IOS разработчика')
    plt.xlabel('Год')
    plt.ylabel('Зарплата, руб')
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "relevance", "dynamics_salary_level_ios_developer_by_years.png"), format="png",
                dpi=300)
    plt.close()


def get_table_dynamics_salary_level_ios_developer_by_years():
    salary_level_ios_developer_by_years = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "salary_level_ios_developer_by_years.csv"), encoding="utf-8")

    salary_level_ios_developer_by_years.columns = ["Год", "Средняя зарплата"]

    table = salary_level_ios_developer_by_years.to_html()

    with open(os.path.join(os.path.dirname(__file__), "table_salary_level_ios_developer_by_years.html"), "w", encoding="utf-8") as file:
        file.write(table)


def get_image_fraction_ios_developer_by_years():
    count_ios_developer_by_years = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_years.csv"), encoding="utf-8")
    fig, sub = plt.subplots(2, 2, figsize=(12, 8))

    x = np.arange(len(count_ios_developer_by_years.index))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.plot(count_ios_developer_by_years["year"], count_ios_developer_by_years["count"], marker="o", linestyle="-", color="b")
    plt.title('Динамика количества вакансий по годам IOS разработчика')
    plt.xlabel('Год')
    plt.ylabel('Количество вакансий')
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "static", "relevance", "dynamics_count_ios_developer_by_years.png"),
                format="png",
                dpi=300)
    plt.close()


def get_table_dynamics_fraction_ios_developer_by_years():
    salary_level_ios_developer_by_years = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "data", "count_ios_developer_by_years.csv"), encoding="utf-8")
    salary_level_ios_developer_by_years.drop(salary_level_ios_developer_by_years.columns[0], axis=1, inplace=True)

    salary_level_ios_developer_by_years.columns = ["Год", "Количество вакансий"]

    table = salary_level_ios_developer_by_years.to_html()

    with open(os.path.join(os.path.dirname(__file__), "table_count_ios_developer_by_years.html"),
              "w", encoding="utf-8") as file:
        file.write(table)


if __name__ == '__main__':
    get_table_dynamics_fraction_ios_developer_by_years()
