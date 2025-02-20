import os

# Lista de nomes dos scripts a serem executados
scripts = [
    "videoProgrammingLanguages.py",
    "incidence_pg.py",
    "popularity_likes_pg.py",
    "popularity_views_pg.py",
    "repetead_videos.py",
    "comparison_beginner_advanced.py",
    "video_duration_analysis",
    "video_tags_analysis"
]

# Loop para executar os scripts em sequência
for script in scripts:
    os.system(f"python3 {script}")
