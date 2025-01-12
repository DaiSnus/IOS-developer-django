# -*- coding: utf-8 -*-


import pandas as pd
import re
import matplotlib.pyplot as plt
import os

file_name = 'vacancies_2024.csv'
vacancy = ['ios'] # Нэйминг вакансии как в Ulearn

output_folder = vacancy[0]

df = pd.read_csv("C:/Users/DaiSnus/Desktop/PythonProjects/pythonProject/.venv/Lib/Django/ios_developer/ios/analitics/data/filtering_vacancies.csv", low_memory=False, encoding="utf-8")
df = df.dropna(subset='key_skills')
df['Год'] = df['published_at'].str.partition('-')[0].astype(int)

df_this_job = df.loc[df['name'].str.contains(vacancy[0], flags=re.IGNORECASE, regex=True)]
for i in range(len(vacancy) - 1):
    df_t = df.loc[df['name'].str.contains(vacancy[i + 1], flags=re.IGNORECASE, regex=True)]
    df_this_job = pd.concat([df_this_job, df_t])

key_skills = df_this_job['key_skills'].tolist()
for i in range(len(key_skills)):
    key_skills[i] = key_skills[i].split('\n')

skills_dict = dict()

for skills in key_skills:
    for skill in skills:
        if skill in skills_dict:
            skills_dict[skill] = skills_dict[skill] + 1
        else:
            skills_dict[skill] = 1

skills_df = pd.DataFrame.from_dict(skills_dict, orient='index', columns=['Кол-во'])
skills_df.index.rename('Навык', inplace=True)
skills_df = skills_df.sort_values(by=['Кол-во'], ascending=False).head(20)
top20 = skills_df.index.values.tolist()
print(top20)
key_skillses = []
for i in range(2015, 2025):
    df = df_this_job.loc[df_this_job['Год'] == i]
    key_skills = df['key_skills'].tolist()
    key_skillses.append(key_skills)

table = pd.DataFrame()
for key_skills in key_skillses:
    for i in range(len(key_skills)):
        key_skills[i] = key_skills[i].split('\n')

    skills_dict = dict()

    for skills in key_skills:
        for skill in skills:
            if skill in skills_dict and skill in top20:
                skills_dict[skill] = skills_dict[skill] + 1
            else:
                skills_dict[skill] = 1

    df = pd.DataFrame.from_dict(skills_dict, orient='index', columns=['Кол-во'])
    df.index.rename('Навык', inplace=True)
    df = df.reset_index()
    df = df.sort_values(by=['Кол-во'], ascending=False).head(20)
    res = (df
           .assign(n=df.groupby("Навык").cumcount())
           .pivot_table(index="n", columns="Навык", values="Кол-во")
           .rename_axis(None))
    table = pd.concat([table, res])

table.reset_index()
table['Год'] = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
max_label_length = 11
short_top20 = [label[:max_label_length] for label in top20]

ax = table.plot(x='Год', y=top20)
ax.legend(short_top20, loc='upper left', fontsize=5)
fig = ax.get_figure()
fig.savefig(os.path.join(os.path.dirname(__file__), 'skills_graph.png'), dpi=300)

# # Таблица по навыкам
text_file = open(os.path.join(os.path.dirname(__file__), "skills_by_year.html"), "w", encoding="utf-8")
html_content = "<table border='1'>\n<tr><th>Год</th>"
for skill in top20:
    html_content += f"<th>{skill}</th>"
html_content += "</tr>\n"
table[top20] = table[top20].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

for index, row in table.iterrows():
    print(row, index)
    html_content += "<tr>"
    html_content += f"<td>{row['Год']}</td>"
    for skill in top20:
        html_content += f"<td>{row[skill]}</td>"
    html_content += "</tr>\n"

html_content += "</table>"

text_file.write(html_content)
text_file.close()
