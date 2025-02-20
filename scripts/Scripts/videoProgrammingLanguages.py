from decouple import config
from db_connection import create_db_connection
import psycopg2
import re
import os
import datetime
import time

# Lista de KEYWORDS
linguagens_populares = {
    "PYTHON", "JAVA", "C", "CPP", "CSHARP", "JAVASCRIPT", "TYPESCRIPT", "PHP", "SHELL", "RUBY", "PROGRAMMING_LANGUAGE_NOT_IDENTIFIED"
}

# Relatórios de execução do Script
if not os.path.exists("relatorios"):
    os.makedirs("relatorios")

report_file_name = f"relatorios/report_videoProgrammingLanguages.txt"

with open(report_file_name, "w") as report_file:
    start_time = time.time()

    conn = create_db_connection()

    cur = conn.cursor()

    cur.execute("SELECT id, title, description, analyzed_as FROM t_video")

    num_rows = 0

    for row in cur.fetchall():
        num_rows += 1
        video_id, title, description, analyzed_as = row
        detected_languages = []

        # Checagem no título do vídeo
        for linguagem in linguagens_populares:
            if linguagem == "C++":
                if re.search(r'\b{}\b'.format(re.escape("C\+\+")), title, re.I):
                    detected_languages.append("CPP")
            elif linguagem == "C#":
                if re.search(r'\b{}\b'.format(re.escape("C#")), title, re.I):
                    detected_languages.append("CSHARP")
            else:
                if re.search(r'\b{}\b'.format(re.escape(linguagem)), title, re.I):
                    detected_languages.append(linguagem)

        # Checagem na descrição do vídeo
        if not detected_languages:
            for linguagem in linguagens_populares:
                if linguagem == "C++":
                    if re.search(r'\b{}\b'.format(re.escape("C\+\+")), description, re.I):
                        detected_languages.append("CPP")
                elif linguagem == "C#":
                    if re.search(r'\b{}\b'.format(re.escape("C#")), description, re.I):
                        detected_languages.append("CSHARP")
                else:
                    if re.search(r'\b{}\b'.format(re.escape(linguagem)), description, re.I):
                        detected_languages.append(linguagem)

        detected_languages = [lang for lang in detected_languages]

        if not detected_languages:
            detected_languages = ["PROGRAMMING_LANGUAGE_NOT_IDENTIFIED"]

        # Atualizando no DB
        if detected_languages:
            first_language = detected_languages[0]
            cur.execute("UPDATE t_video SET analyzed_as = %s WHERE id = %s", (first_language, video_id))
            conn.commit()

    end_time = time.time()
    duration = end_time - start_time

    # Report
    report_file.write(f"Script executado com sucesso.\n")
    report_file.write(f"Data e hora da execução: {datetime.datetime.now()}\n")
    report_file.write(f"Tempo de início: {datetime.datetime.fromtimestamp(start_time)}\n")
    report_file.write(f"Tempo de fim: {datetime.datetime.fromtimestamp(end_time)}\n")
    report_file.write(f"Duração da execução: {duration:.2f} segundos\n")
    report_file.write(f"Número de registros processados: {num_rows}\n")


cur.close()
conn.close()
