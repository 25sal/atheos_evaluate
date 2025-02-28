from collections import defaultdict
import os
import subprocess

import numpy as np


def run_git_command(repo_path, command):
    """ Esegue un comando Git e ritorna l'output """
    result = subprocess.run(
        command,
        cwd=repo_path,
        shell=True,
        text=True,
        capture_output=True
    )
    return result.stdout.strip()



def get_average_commit_interval_from_logs(repo_path):
    """ Calcola il tempo medio tra commit e la durata totale di lavoro usando il file .git/logs/HEAD """
    
    logs_path = os.path.join(repo_path, "logs", "HEAD")

    if not os.path.exists(logs_path):
        return {"error": "Il file di log non esiste"}

    timestamps = []

    # Leggiamo il file HEAD e estraiamo i timestamp
    with open(logs_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    timestamp = int(parts[4])  # Il timestamp è nella sesta colonna
                    timestamps.append(timestamp)
                except ValueError:
                    continue

    # Se abbiamo meno di due timestamp, non possiamo calcolare nulla
    if len(timestamps) < 2:
        return {"error": "Non ci sono abbastanza commit per il calcolo"}

    # Ordiniamo i timestamp
    timestamps = sorted(timestamps)

    # Durata totale: Ultimo timestamp meno il secondo (ignorando la creazione repo)
    total_work_duration = timestamps[-1] - timestamps[1]

    # Calcoliamo la differenza tra ogni commit per ottenere l'intervallo medio
    intervals = [timestamps[i] - timestamps[i - 1] for i in range(2, len(timestamps))]
    
    if not intervals:
        return {"error": "Non ci sono abbastanza commit validi"}

    avg_interval = sum(intervals) / len(intervals)

    return {
        "total_work_duration": round(total_work_duration/60, 2),  # Convertito in minuti
        "average_commit_interval": round(avg_interval/60, 2),  # Convertito in minuti
        "commit_count": len(intervals) +1
    }



def detect_large_commit_spike(repo_path, threshold_multiplier=3.5):
    """ 
    Analizza commit per commit e verifica se ci sono aumenti improvvisi del numero di righe aggiunte.
    Un commit è sospetto se ha un numero di righe aggiunte molto più alto rispetto alla media dei commit precedenti.
    Restituisce `True` se almeno un commit è sospetto e una lista dei commit sospetti.
    """
    output = run_git_command(repo_path, "git log --numstat --pretty='%H'")

    lines_added_per_commit = []
    commit_hashes = []
    current_commit = None
    current_lines_added = 0

    for line in output.split("\n"):
        parts = line.split("\t")

        if len(parts) == 3 and parts[0].isdigit():
            current_lines_added += int(parts[0])  # Somma le righe aggiunte per commit
        elif len(line) == 40:  # Se è un hash di commit
            if current_commit:
                lines_added_per_commit.append((current_commit, current_lines_added))
            current_commit = line  # Nuovo commit hash
            current_lines_added = 0  # Reset conteggio

    if current_commit:
        lines_added_per_commit.append((current_commit, current_lines_added))

    if len(lines_added_per_commit) < 3:  # Se ci sono pochi commit, non facciamo analisi
        return False, []

    # 🔹 **Filtriamo i commit con zero righe aggiunte per evitare che la media sia falsata**
    added_lines_list = [entry[1] for entry in lines_added_per_commit if entry[1] > 0]

    # Se tutti i commit hanno 0 righe aggiunte, non possiamo calcolare la media
    if len(added_lines_list) < 2:
        return False, []

    # Calcola media e deviazione standard delle righe aggiunte per commit
    mean_lines = np.mean(added_lines_list)
    std_lines = np.std(added_lines_list)

    suspicious_commits = []
    is_suspicious = False

    for commit_hash, lines_added in lines_added_per_commit:
        if lines_added > mean_lines + (threshold_multiplier * std_lines):
            suspicious_commits.append({"commit": commit_hash, "lines_added": lines_added})
            is_suspicious = True

    return is_suspicious



def get_lines_modified(repo_path):
    """ Conta il numero totale di linee aggiunte e rimosse """
    output = run_git_command(repo_path, "git log --numstat --pretty='%H'")
    lines_added = 0
    lines_removed = 0

    for line in output.split("\n"):
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            lines_added += int(parts[0])
            lines_removed += int(parts[1])
    print(repo_path,lines_added, lines_removed)
    return {"lines_added": lines_added, "lines_removed": lines_removed}



def check_code_similarity(repo_path):
    """ Confronta l'ultimo commit con il penultimo per verificare plagio """
    output = run_git_command(repo_path, "git diff HEAD~1 HEAD")
    similarity_score = 100 - (len(output) / 5000 * 100)  # Formula di somiglianza base

    return max(0, min(similarity_score, 100))



def get_lines_modified_per_commit(repo_path):
    """ Restituisce il numero di linee aggiunte e rimosse per ogni commit, ignorando cambi di formattazione. """
    output = run_git_command(repo_path, "git log --numstat --pretty=format:'%H'")
    commits = []
    current_commit = None

    for line in output.split("\n"):
        if len(line) == 40:  # Se la riga è un hash di commit (SHA-1)
            if current_commit:
                # Filtra commit con sole modifiche di formattazione (zero cambi reali)
                if current_commit["lines_added"] > 0 or current_commit["lines_removed"] > 0:
                    commits.append(current_commit)  
            current_commit = {"commit": line, "lines_added": 0, "lines_removed": 0}
        else:
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                file_path = parts[2]

                # Controlla se il diff è solo di formattazione
                #diff_output = run_git_command(repo_path, f"git diff -w --ignore-space-at-eol HEAD~1 HEAD -- {file_path}")
                #if diff_output.strip():  # Se il diff contiene modifiche reali
                current_commit["lines_added"] += int(parts[0])
                current_commit["lines_removed"] += int(parts[1])

    if current_commit and (current_commit["lines_added"] > 0 or current_commit["lines_removed"] > 0):
        commits.append(current_commit)

    return commits



