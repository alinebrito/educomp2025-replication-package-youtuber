from decouple import config
import psycopg2
import matplotlib.pyplot as plt
from db_connection import create_db_connection
import os
import datetime
import time  

def get_video_counts():
    conn = create_db_connection()
    cur = conn.cursor()

    query = """
        SELECT COUNT(*) AS total, COUNT(DISTINCT video_id) AS distintos, COUNT(*) - COUNT(DISTINCT video_id) AS repetidos
        FROM t_video
    """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results[0]

def generate_video_count_plot(data):
    total, distintos, repetidos = data

    categories = ['Total', 'Distintos', 'Repetidos']
    counts = [total, distintos, repetidos]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, counts)
    plt.xlabel('Categorias')
    plt.ylabel('Contagem de Vídeos')
    plt.title('Número Total de Vídeos, Vídeos Distintos e Vídeos Repetidos')

    # Adiciona os valores acima das barras
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha='center', va='bottom', fontsize=14, color='black')

    output_directory = 'plots'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_plot_path = os.path.join(output_directory, 'total_videos_distintos_repetidos.png')
    plt.savefig(output_plot_path)
    plt.show()

start_time = time.time()
report_file_name = f"relatorios/report_videos_repetidos.txt"

video_data = get_video_counts()
generate_video_count_plot(video_data)

end_time = time.time()
duration = end_time - start_time

with open(report_file_name, "w") as report_file:
    report_file.write(f"Script iniciado com sucesso.\n")
    report_file.write(f"Data e hora do inicio da execucao: {datetime.datetime.now()}\n")
    report_file.write(f"Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}\n")
    report_file.write(f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
    report_file.write(f"Duracao da execucao: {duration:.2f} segundos\n")
    report_file.write(f"Numero de Videos Totais: {video_data[0]}\n")
    report_file.write(f"Numero de Videos Distintos: {video_data[1]}\n")
    report_file.write(f"Numero de Videos Repetidos: {video_data[2]}\n")

print("Relatório e gráfico gerados com sucesso.")
