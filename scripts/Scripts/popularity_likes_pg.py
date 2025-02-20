from decouple import config
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
        SELECT t_video.analyzed_as, t_statistics.like_count
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

def calculate_medians(data, unique_labels):
    medians = []
    for label in unique_labels:
        median_val = data[data['analyzed_as'] == label]['like_count'].median()
        medians.append(median_val)
    return medians

def generate_seaborn_boxplot(data, output_folder):
    df = pd.DataFrame(data, columns=['analyzed_as', 'like_count'])
    df['like_count'] = df['like_count'].astype(float)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.figure(figsize=(16, 9))
    sns.set(style="whitegrid")

    ax = sns.boxplot(x='analyzed_as', y='like_count', data=df, showfliers=False)

    plt.yscale('log')  
    plt.xlabel('Linguagem de Programação', fontsize=16)
    plt.ylabel('Número de likes', fontsize=16)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=16)

    unique_labels = df['analyzed_as'].unique()
    medians = calculate_medians(df, unique_labels)

    # Adiciona a mediana acima de cada boxplot individual
    for i, label in enumerate(unique_labels):
        ax.text(i, medians[i], f'{medians[i]:.2f}', ha='center', va='bottom', fontsize=16, color='black')

    output_path = os.path.join(output_folder, 'geral_boxplots_likes.png')
    plt.savefig(output_path)
    plt.close()


if __name__ == '__main__':
    start_time = time.time()

    likes_data = get_data()

    output_folder = 'boxplots/likes'  
    generate_seaborn_boxplot(likes_data, output_folder)

    end_time = time.time()
    duration = end_time - start_time

    with open("relatorios/report_likes.txt", "w") as report_file:
        report_file.write(f"Script iniciado com sucesso.\n")
        report_file.write(f"Data e hora da execucao: {datetime.datetime.now()}\n")
        report_file.write(f"Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}\n")
        report_file.write(f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
        report_file.write(f"Duracao da execucao: {duration:.2f} segundos\n")

    print("Relatório e gráficos de boxplot com anotações gerados com sucesso.")
