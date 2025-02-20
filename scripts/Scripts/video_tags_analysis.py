import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from decouple import config
from db_connection import create_db_connection
import datetime
import time
from scipy.stats import mannwhitneyu


def get_data_top25_tags():
    conn = create_db_connection()
    cur = conn.cursor()

    query = """
        SELECT ranked_videos.video_id, COUNT(*) as tag_count
        FROM (
            SELECT vd.id AS video_id, 
                ROW_NUMBER() OVER (ORDER BY s.view_count DESC) as row_num,
                COUNT(*) OVER () as total_rows
            FROM t_video_distinct vd
            JOIN t_statistics s ON vd.fk_statistics = s.id
            WHERE s.view_count IS NOT NULL
        ) AS ranked_videos
        JOIN t_video_tags vt ON ranked_videos.video_id = vt.video_id
        WHERE row_num <= total_rows * 0.25
        GROUP BY ranked_videos.video_id;
    """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


def get_data_bottom25_tags():
    conn = create_db_connection()
    cur = conn.cursor()

    query = """
        SELECT ranked_videos.video_id, COUNT(*) as tag_count
        FROM (
            SELECT vd.id AS video_id, 
                ROW_NUMBER() OVER (ORDER BY s.view_count ASC) as row_num,
                COUNT(*) OVER () as total_rows
            FROM t_video_distinct vd
            JOIN t_statistics s ON vd.fk_statistics = s.id
            WHERE s.view_count IS NOT NULL
        ) AS ranked_videos
        JOIN t_video_tags vt ON ranked_videos.video_id = vt.video_id
        WHERE row_num <= total_rows * 0.25
        GROUP BY ranked_videos.video_id;
    """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

# Função para adicionar anotação da mediana ao gráfico


def add_median_annotation(ax, data, color):
    median_val = data.median()
    min_val = data.min()
    max_val = data.max()

    ax.text(0.5, 0.95, f'Mediana: {median_val:.2f}', horizontalalignment='center', verticalalignment='top',
            transform=ax.transAxes, fontsize=18, color=color)

    return min_val, max_val, median_val


def mann_whitney_test_tags(data1, data2):
    stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
    result = "Significativo" if p_value < 0.05 else "Não Significativo"

    return stat, p_value, result


if __name__ == '__main__':
    start_time = time.time()

    output_folder = 'boxplots/video_tags'

    # Obtém os dados
    tag_count_top25_data = get_data_top25_tags()
    tag_count_bottom25_data = get_data_bottom25_tags()

    # Transforma a lista de tuplas em uma lista de listas
    tag_count_top25_data = list(tag_count_top25_data)
    tag_count_bottom25_data = list(tag_count_bottom25_data)

    # Cria um DataFrame a partir do conjunto de dados
    data_quartil = 11413
    df_tags_top = pd.DataFrame(tag_count_top25_data, columns=[
                               'video_id', 'tag_count'])

    for i in range(int(df_tags_top.size/2), data_quartil):
        df_tags_top.loc[len(df_tags_top.index)] = ['x', 0]

    df_tags_bottom = pd.DataFrame(tag_count_bottom25_data, columns=[
                                  'video_id', 'tag_count'])

    for i in range(int(df_tags_bottom.size/2), data_quartil):
        df_tags_bottom.loc[len(df_tags_bottom.index)] = ['x', 0]

    # Configuração do tamanho do gráfico
    plt.figure(figsize=(12, 6))

    # Gera o boxplot usando seaborn
    ax_tags_top = sns.boxplot(x=df_tags_top['tag_count'], color='blue')

    # Adiciona rótulos aos eixos
    plt.xlabel('Contagem de Tags', fontsize=18)
    plt.ylabel('Valores', fontsize=18)

    # Adiciona mediana ao gráfico
    add_median_annotation(ax_tags_top, df_tags_top['tag_count'], 'blue')

    min_val_top, max_val_top, median_val_top = add_median_annotation(
        ax_tags_top, df_tags_top['tag_count'], 'blue')

    # Exibe o gráfico
    plt.show()

    plt.figure(figsize=(12, 6))
    ax_tags_bottom = sns.boxplot(x=df_tags_bottom['tag_count'], color='orange')
    plt.xlabel('Contagem de Tags', fontsize=18)
    plt.ylabel('Valores', fontsize=18)
    add_median_annotation(
        ax_tags_bottom, df_tags_bottom['tag_count'], 'orange')
    plt.show()

    min_val_bottom, max_val_bottom, median_val_bottom = add_median_annotation(
        ax_tags_bottom, df_tags_bottom['tag_count'], 'orange')

    df_tags_top['tag_count'] = df_tags_top['tag_count'].astype(int)
    df_tags_bottom['tag_count'] = df_tags_bottom['tag_count'].astype(int)

    stat_tags, p_value_tags, result_tags = mann_whitney_test_tags(
        df_tags_top['tag_count'], df_tags_bottom['tag_count']
    )

    end_time = time.time()
    duration = end_time - start_time

    with open("relatorios/report_video_tags.txt", "w") as report_file:
        report_file.write(f"Script iniciado com sucesso.\n")
        report_file.write(
            f"Data e hora da execucao: {datetime.datetime.now()}\n")
        report_file.write(f"Minimo Top 25%: {min_val_top:.2f}\n")
        report_file.write(f"Maximo Top 25%: {max_val_top:.2f}\n")
        report_file.write(f"Mediana Top 25%: {median_val_top:.2f}\n")
        report_file.write(f"Minimo Bottom 25%: {min_val_bottom:.2f}\n")
        report_file.write(f"Maximo Bottom 25%: {max_val_bottom:.2f}\n")
        report_file.write(f"Mediana Bottom 25%: {median_val_bottom:.2f}\n")
        report_file.write(f"U Statistic (Tags): {stat_tags:.2f}\n")
        report_file.write(f"P-Value (Tags): {p_value_tags:.4f}\n")
        report_file.write(f"Resultado (Tags): {result_tags}\n")
        report_file.write(
            f"Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}\n")
        report_file.write(
            f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
        report_file.write(f"Duracao da execucao: {duration:.2f} segundos\n")

    print("Relatorio e graficos de boxplot com anotacoes gerados com sucesso.")
