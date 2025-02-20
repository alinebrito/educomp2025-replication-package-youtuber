import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from decouple import config
import psycopg2
from db_connection import create_db_connection
import os
import datetime
import time
from scipy.stats import mannwhitneyu


def get_data(query):
    conn = create_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(query)
        results = cur.fetchall()
        return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def add_median_annotation(ax, data, color):
    median_val = data.median()
    min_val = data.min()
    max_val = data.max()

    ax.text(0.5, 0.95, f'Mediana: {median_val:.2f}', horizontalalignment='center', verticalalignment='top',
            transform=ax.transAxes, fontsize=16, color=color)

    return min_val, max_val, median_val


def create_boxplot(data, color, label):
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(x=data, color=color)
    plt.xlabel('Duração do Vídeo (segundos)', fontsize=16)
    plt.ylabel('Valores', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    min_val, max_val, median_val = add_median_annotation(ax, data, color)

    plt.title(f'Boxplot - {label}', fontsize=18)
    plt.show()

    return min_val, max_val, median_val


def mann_whitney_test(data1, data2):
    stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
    result = "Significativo" if p_value < 0.05 else "Não Significativo"

    return stat, p_value, result


if __name__ == '__main__':
    start_time = time.time()

    query_top25 = """
        SELECT video_duration 
        FROM (
            SELECT s.video_duration, 
                   ROW_NUMBER() OVER (ORDER BY s.view_count DESC) as row_num,
                   COUNT(*) OVER () as total_rows
            FROM t_video vd
            JOIN t_statistics s ON vd.fk_statistics = s.id
            WHERE s.video_duration IS NOT NULL
            AND s.view_count IS NOT NULL
        ) AS ranked_videos
        WHERE row_num <= total_rows * 0.25;
    """

    query_bottom25 = """
        SELECT video_duration 
        FROM (
            SELECT s.video_duration, 
                   ROW_NUMBER() OVER (ORDER BY s.view_count ASC) as row_num,
                   COUNT(*) OVER () as total_rows
            FROM t_video vd
            JOIN t_statistics s ON vd.fk_statistics = s.id
            WHERE s.video_duration IS NOT NULL
            AND s.view_count IS NOT NULL
        ) AS ranked_videos
        WHERE row_num <= total_rows * 0.25;
    """

    video_duration_top25_data = get_data(query_top25)
    video_duration_bottom25_data = get_data(query_bottom25)

    if video_duration_top25_data and video_duration_bottom25_data:
        video_duration_top25_data = [item[0]
                                     for item in video_duration_top25_data]
        video_duration_bottom25_data = [item[0]
                                        for item in video_duration_bottom25_data]

        output_folder = 'boxplots/video_duration'

        df_top = pd.DataFrame({'video_duration': video_duration_top25_data})
        df_bottom = pd.DataFrame(
            {'video_duration': video_duration_bottom25_data})

    min_val_top, max_val_top, median_val_top = create_boxplot(
        df_top['video_duration'], 'blue', 'Top 25%')
    min_val_bottom, max_val_bottom, median_val_bottom = create_boxplot(
        df_bottom['video_duration'], 'orange', 'Bottom 25%')

    df_top['video_duration'] = df_top['video_duration'].astype(int)
    df_bottom['video_duration'] = df_bottom['video_duration'].astype(int)
    # Mann-Whitney U Test
    stat, p_value, result = mann_whitney_test(df_top['video_duration'],
                                              df_bottom['video_duration'])

    end_time = time.time()
    duration = end_time - start_time

    with open("relatorios/report_video_duration.txt", "w") as report_file:
        report_content = f"""
            Script iniciado com sucesso.
            Data e hora da execucao: {datetime.datetime.now()}
            Duracao da execucao: {duration:.2f} segundos
            Miimo Top 25%: {min_val_top:.2f}
            Maximo Top 25%: {max_val_top:.2f}
            Mediana Top 25%: {median_val_top:.2f}
            Minimo Bottom 25%: {min_val_bottom:.2f}
            Maximo Bottom 25%: {max_val_bottom:.2f}
            Mediana Bottom 25%: {median_val_bottom:.2f}
            U Statistic: {stat:.2f}
            P-Value: {p_value:.4f}
            Resultado: {result}
            Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}
            Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}
        """
        report_file.write(report_content)

    print("Relatório e gráficos de boxplot com anotações gerados com sucesso.")
