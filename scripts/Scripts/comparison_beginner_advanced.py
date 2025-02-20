from decouple import config
import psycopg2
import matplotlib.pyplot as plt
from db_connection import create_db_connection
import os
import datetime
import time

KEYWORDS_INICIANTES = [
    'Start', 'Started', 'Starter', 'Starting', 'Beginning', 'Begin', 'Beginner', 'Entry', 'Learn'
]

KEYWORDS_AVANCADOS = ['Advanced', 'Advance', 'Complex', 'Difficult', 'Elaborated', 'Hard']

sorted_languages = []  
begginers_counts = {}  
advanced_counts = {}

def get_data():
    conn = create_db_connection()
    cur = conn.cursor()

    query = """
        SELECT DISTINCT ON (video_id) analyzed_as, title 
        FROM t_video 
        WHERE analyzed_as NOT IN ('OTHER', 'PROGRAMMING_LANGUAGE_NOT_IDENTIFIED')
    """

    cur.execute(query)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

def count_keywords(titles, keywords):
    count = 0
    for title in titles:
        title_str = title[1] if title[1] else ''
        title_str_lower = title_str.lower()
        for keyword in keywords:
            if keyword.lower() in title_str_lower:
                count += 1
                break
    return count

def plot_comparison(data):
    global sorted_languages, begginers_counts, advanced_counts 

    language_counts = {}  

    for language, title in data:
        title_str = title if title else ''
        title_str_lower = title_str.lower()
        
        if language not in language_counts:
            language_counts[language] = {'Iniciantes': 0, 'Avançados': 0}
        
        for keyword in KEYWORDS_INICIANTES:
            if keyword.lower() in title_str_lower:
                language_counts[language]['Iniciantes'] += 1
                break
        
        for keyword in KEYWORDS_AVANCADOS:
            if keyword.lower() in title_str_lower:
                language_counts[language]['Avançados'] += 1
                break

    sorted_languages = sorted(language_counts.keys(), key=lambda lang: language_counts[lang]['Iniciantes'] + language_counts[lang]['Avançados'], reverse=True)

    plt.figure(figsize=(12, 6))
    x = range(len(sorted_languages))
    width = 0.4  

    for language in sorted_languages:
        begginers_counts[language] = language_counts[language]['Iniciantes']
        advanced_counts[language] = language_counts[language]['Avançados']

    bars1 = plt.bar([i - width/2 for i in x], begginers_counts.values(), width, label='Iniciantes')
    bars2 = plt.bar([i + width/2 for i in x], advanced_counts.values(), width, label='Avançados')

    plt.ylabel('Número de Vídeos', fontsize=16)
    plt.yticks(fontsize=16)
    plt.xticks(x, sorted_languages, rotation=45, ha='right', fontsize=16) 
    plt.legend(fontsize=16)

    # Adiciona os valores acima das barras
    for bar in bars1:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom', fontsize=12)

    for bar in bars2:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom', fontsize=12)

    output_directory = 'plots/distintos'  
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, 'comparacao_por_linguagem.png')
    plt.savefig(output_path)
    plt.show()

start_time = time.time()

video_data = get_data()
plot_comparison(video_data)

end_time = time.time()
duration = end_time - start_time

output_directory = 'relatorios'  
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

with open(os.path.join(output_directory, "report_beginner_advanced.txt"), "w") as report_file:
    report_file.write(f"Script iniciado com sucesso.\n")
    report_file.write(f"Data e hora da execucao: {datetime.datetime.now()}\n")
    report_file.write(f"Tempo de inicio: {datetime.datetime.fromtimestamp(start_time)}\n")
    report_file.write(f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
    report_file.write(f"Duracao da execucao: {duration:.2f} segundos\n")

with open(os.path.join(output_directory, "valores_avancados_iniciantes.txt"), "w") as valores_file:
    for language in sorted_languages:
        valores_file.write(f"Linguagem: {language}\n")
        valores_file.write(f"Iniciantes: {begginers_counts[language]}\n")
        valores_file.write(f"Avancados: {advanced_counts[language]}\n")
        valores_file.write("\n")

print("Relatório gerado com sucesso.")
