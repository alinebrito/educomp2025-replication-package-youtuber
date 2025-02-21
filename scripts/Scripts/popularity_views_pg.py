from decouple import config
import psycopg2
import seaborn as sns
import matplotlib.pyplot as plt
from db_connection import create_db_connection
import os
import pandas as pd
import datetime
import time


def get_data():
    conn = create_db_connection()
    cur = conn.cursor()

    query = """
        SELECT t_video.analyzed_as, t_statistics.view_count
        FROM t_video
        JOIN t_statistics ON t_video.fk_statistics = t_statistics.id
        WHERE t_video.video_id IN (SELECT DISTINCT ON (video_id) video_id FROM t_video)
        AND t_video.analyzed_as NOT IN ('PROGRAMMING_LANGUAGE_NOT_IDENTIFIED', 'OTHER')
    """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


def generate_seaborn_boxplot(data, output_folder):
    df = pd.DataFrame(data, columns=['analyzed_as', 'view_count'])
    df['view_count'] = df['view_count'].astype(float)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.figure(figsize=(16, 9))
    sns.set(style="whitegrid")

    ax = sns.boxplot(x='analyzed_as', y='view_count', data=df, showfliers=False)

    plt.yscale('log')
    plt.xlabel('Linguagem de Programação', fontsize=16)
    plt.ylabel('Número de views', fontsize=16)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=16)

    unique_languages = df['analyzed_as'].unique()

    # Adiciona a mediana acima de cada boxplot individual
    for i, language in enumerate(unique_languages):
        median = df[df['analyzed_as'] == language]['view_count'].median()
        ax.text(i, median * 1.02, f'{median:.2f}', ha='center', va='bottom', fontsize=14, color='black')

    output_path = os.path.join(output_folder, 'geral_boxplots_views.png')
    plt.savefig(output_path)
    plt.close()

if __name__ == '__main__':
    start_time = time.time()

    views_data = get_data()

    output_folder = 'boxplots/views'
    generate_seaborn_boxplot(views_data, output_folder)

    end_time = time.time()
    duration = end_time - start_time

    with open("relatorios/report_views.txt", "w") as report_file:
        report_file.write(f"Script iniciado com sucesso.\n")
        report_file.write(
            f"Data e hora da execucao: {datetime.datetime.now()}\n")
        report_file.write(
            f"Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}\n")
        report_file.write(
            f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
        report_file.write(f"Duracao da execucao: {duration:.2f} segundos\n")

    print("Relatório e gráficos de boxplot com anotações gerados com sucesso.")
