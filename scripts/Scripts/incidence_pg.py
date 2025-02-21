from decouple import config
import psycopg2
import matplotlib.pyplot as plt
from db_connection import create_db_connection
import os
import datetime
import time

def get_video_counts(distinct=False):
    conn = create_db_connection()
    cur = conn.cursor()

    if distinct:
        query = """
            SELECT analyzed_as, COUNT(DISTINCT video_id) AS count
            FROM t_video
            WHERE analyzed_as NOT IN ('PROGRAMMING_LANGUAGE_NOT_IDENTIFIED')
            GROUP BY analyzed_as
            ORDER BY count DESC
        """
    else:
        query = """
            SELECT analyzed_as, COUNT(*) AS count
            FROM t_video
            WHERE analyzed_as NOT IN ('PROGRAMMING_LANGUAGE_NOT_IDENTIFIED')
            GROUP BY analyzed_as
            ORDER BY count DESC
        """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

def generate_language_incidence_plot(data, folder_name, label):
    if not data:
        return

    languages, counts = zip(*data)

    plt.figure(figsize=(12, 6))
    bars = plt.bar(languages, counts)
    plt.xlabel('Linguagem de Programação', fontsize=16)
    plt.ylabel('Número de vídeos mencionados', fontsize=16)
    plt.xticks(rotation=0, fontsize=14)  # Ajuste de tamanho de fonte nos rótulos do eixo x
    plt.yticks(fontsize=14)  # Ajuste de tamanho de fonte nos rótulos do eixo y

    # Adiciona anotações de valor máximo no gráfico
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, count, f'{count}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()

    output_directory = os.path.join('plots', folder_name)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, f'ocorrencia_linguagens_{folder_name}.png')

    # Salvar o gráfico
    plt.savefig(output_path)
    plt.show()

def generate_report(data_distinct, data_total):
    start_time = time.time()
    report_file_name = f"relatorios/report_ocorrencia_linguagens.txt"

    with open(report_file_name, "w") as report_file:
        report_file.write(f"Script iniciado com sucesso.\n")
        report_file.write(f"Data e hora da execucao: {datetime.datetime.now()}\n")

        report_file.write("Ocorrencia de Linguagens de Programacao em videos do YouTube (Distintos):\n")
        for language, count in data_distinct:
            report_file.write(f"{language}: {count}\n")

        report_file.write("Ocorrencia de Linguagens de Programacao em videos do YouTube (Totais):\n")
        for language, count in data_total:
            report_file.write(f"{language}: {count}\n")

    end_time = time.time()
    duration = end_time - start_time

    print("Relatorio e gráficos gerados com sucesso.")

distinct_data = get_video_counts(distinct=True)
generate_language_incidence_plot(distinct_data, 'distintos', 'Distintos')

total_data = get_video_counts()
generate_language_incidence_plot(total_data, 'totais', 'Totais')

generate_report(distinct_data, total_data)
