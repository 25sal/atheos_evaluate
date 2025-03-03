from collections import defaultdict
import time
from flask import jsonify, render_template, redirect, url_for, flash, request, session, make_response, send_file, Blueprint
import pandas as pd
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import csv
from app.config import Config
from app.models.base import list_res_accounts, delete_res_accounts, delete_all, list_logged_accounts, list_projects
import app.models.base as model_base
from app.utils.admin import import_reservations, gen_passwords, add_atheos_users, create_random_projects, update_atheos_projects, create_prj_dirs, restrict_atheos_acl, delete_prj_dirs, hash_password, update_atheos_user, delete_user_dirs, delete_atheos_projects, delete_atheos_user
# Create a permission with a single Need, in this case a RoleNeed.
from flask_principal import Permission, RoleNeed
import numpy as np
import subprocess
from app.routes.git_analisys import get_average_commit_interval_from_logs, get_lines_modified_per_commit, detect_large_commit_spike
import re
import requests


admin_role = Permission(RoleNeed('admin'))

admin_bp =  Blueprint('admin_blueprint', __name__)

@admin_bp.route('/admin', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_index():
    return render_template("admin/index.html")


BASE_DIR = "/home/evaluatex/users"  # Cartella base degli utenti


@admin_bp.route('/api/detect-ai')
def detect_ai_all():
    """ Controlla tutti gli studenti e restituisce quelli con codice sospetto generato da AI """
    ai_detected_users = []

    for username in os.listdir(BASE_DIR):
        user_path = os.path.join(BASE_DIR, username, "c")
        if not os.path.isdir(user_path):
            continue

        subfolders = [f for f in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, f)) and f != "sandbox"]
        if not subfolders:
            continue

        valid_folder = os.path.join(user_path, subfolders[0])
        c_files = [f for f in os.listdir(valid_folder) if f.endswith(".c")]
        if not c_files:
            continue

        c_file_path = os.path.join(valid_folder, c_files[0])
        analysis_result = detect_ai_generated_code(c_file_path)

        if analysis_result["is_ai_generated"]:
            ai_detected_users.append({
                "username": username,
                "avg_function_length": analysis_result["avg_function_length"],
                "comment_ratio": analysis_result["comment_ratio"],
            })

    return jsonify(ai_detected_users)


@admin_bp.route('/api/get-code/<username>', methods=['GET'])
def get_user_code(username):
    """ Restituisce il contenuto del file .c di uno studente """
    user_path = os.path.join(BASE_DIR, username, "c")

    if not os.path.isdir(user_path):
        return jsonify({"error": "User not found"}), 404

    subfolders = [f for f in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, f)) and f != "sandbox"]
    if not subfolders:
        return jsonify({"error": "No valid folder found"}), 404

    valid_folder = os.path.join(user_path, subfolders[0])
    
    # Trova il file .c
    c_files = [f for f in os.listdir(valid_folder) if f.endswith(".c")]
    if not c_files:
        return jsonify({"error": "No C file found"}), 404

    c_file_path = os.path.join(valid_folder, c_files[0])

    # Leggiamo il file e restituiamo il contenuto
    try:
        with open(c_file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
        return jsonify({"filename": c_files[0], "content": code_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def detect_ai_generated_code_old(file_path):
    """ Analizza il codice e verifica se è stato scritto da un'AI """
    
    # Legge il codice sorgente
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 🔹 1. Controllo della Complessità (Lunghezza media delle funzioni)
    functions = re.findall(r'\w+\s+\w+\(.*?\)\s*{', code, re.DOTALL)
    avg_function_length = sum(len(f) for f in functions) / max(len(functions), 1)

    # 🔹 2. Controllo dei Commenti (ChatGPT tende a scrivere molti commenti dettagliati)
    comments = re.findall(r'//.*?$|/\*.*?\*/', code, re.DOTALL | re.MULTILINE)
    comment_ratio = len(comments)

    # 🔹 3. Controllo di Pattern di ChatGPT (Uso eccessivo di printf, scanf)
    #ai_patterns = [r"// Function to", r"/\*.*?\*/", r"printf\(", r"scanf\(", r"main\s*\(\)\s*\{"]  
    #ai_match_count = sum(len(re.findall(pattern, code)) for pattern in ai_patterns)

    # 🔹 4. Controllo con un AI Detector (GPTZero o OpenAI API)
    #try:
    #    headers = {"Authorization": f"Bearer YOUR_OPENAI_API_KEY"}
    #    response = requests.post("https://api.openai.com/v1/moderations", headers=headers, json={"input": code})
    #    ai_score = response.json()["results"][0]["flagged"]
    #except:
    #    ai_score = False  # Se non possiamo connetterci all'API, ignora questo passaggio

    # 🔹 5. Determinazione finale (Soglia per considerare AI)
    #is_ai_generated = (avg_function_length > 200 or comment_ratio > 5)

    return {
        "avg_function_length": avg_function_length,
        "comment_ratio": comment_ratio,
        #"ai_match_count": ai_match_count,
        #"ai_score": ai_score,
        #"is_ai_generated": is_ai_generated
    }




@admin_bp.route("/api/upload-excel", methods=["POST"])
def upload_excel():
    """Gestisce il caricamento dell'Excel e cancella le cartelle utenti con codice 'ASS'."""
    if "file" not in request.files:
        return jsonify({"message": "Nessun file caricato!"}), 400

    file = request.files["file"]

    # Verifica che sia un file Excel
    if not file.filename.endswith((".xls", ".xlsx")):
        return jsonify({"message": "Formato file non valido! Caricare un file Excel."}), 400

    try:
        df = pd.read_excel(file)  # Legge l'Excel

        # Verifica che il file abbia almeno 9 colonne (indice 8 per colonna I, indice 2 per colonna C)
        if df.shape[1] < 9:
            return jsonify({"message": "Errore: il file Excel deve avere almeno 9 colonne!"}), 400

        deleted_users = []

        # Scansiona ogni riga e controlla la colonna all'indice 8 ("I")
        for index, row in df.iterrows():
            if str(row.iloc[8]).strip().upper() == "ASS":  # Colonna "I" con indice 8
                user_folder = os.path.join(BASE_DIR, str(row.iloc[2]).strip())  # Colonna "C" con indice 2

                if os.path.exists(user_folder):
                    os.system(f"rm -rf {user_folder}")  # Elimina la cartella utente
                    deleted_users.append(str(row.iloc[2]).strip())

        return jsonify({"message": f"Rimosse {len(deleted_users)} cartelle utenti!", "deleted_users": deleted_users})

    except Exception as e:
        return jsonify({"message": f"Errore nel processamento del file: {str(e)}"}), 500
    
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# BASE_DIR deve essere definito, ad esempio:
# BASE_DIR = "/path/to/users"

# Supponiamo che detect_large_commit_spike e get_average_commit_interval_from_logs siano definite altrove
# ad esempio:
# def detect_large_commit_spike(repo_path, threshold_multiplier=3.5): ...
# def get_average_commit_interval_from_logs(repo_path): ...

def detect_ai_generated_code(file_path):
    """ 
    Analizza il codice e verifica se è stato scritto da un'AI.
    Legge il file con gestione degli errori di decodifica.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            code = f.read()
    except Exception:
        code = ""
    
    # 🔹 1. Controllo della Complessità (Lunghezza media delle funzioni)
    functions = re.findall(r'\w+\s+\w+\(.*?\)\s*{', code, re.DOTALL)
    avg_function_length = sum(len(f) for f in functions) / max(len(functions), 1)
    
    # 🔹 2. Controllo dei Commenti
    comments = re.findall(r'//.*?$|/\*.*?\*/', code, re.DOTALL | re.MULTILINE)
    comment_ratio = len(comments)
    
    return {
        "avg_function_length": avg_function_length,
        "comment_ratio": comment_ratio
    }

def process_user(user):
    """
    Elabora le metriche per un singolo utente.
    All'interno di questo processo, utilizza un ThreadPoolExecutor per parallelizzare:
      - l'analisi dei commit sospetti (detect_large_commit_spike)
      - il calcolo degli intervalli medi (get_average_commit_interval_from_logs)
      - l'analisi del codice sorgente (detect_ai_generated_code)
    Ritorna una tupla (user, user_data) oppure None se l'utente non è valido.
    """
    user_path = os.path.join(BASE_DIR, user, "c")
    if not os.path.isdir(user_path):
        return None

    subfolders = [f for f in os.listdir(user_path)
                  if os.path.isdir(os.path.join(user_path, f)) and f != "sandbox"]
    if not subfolders:
        return None

    repo_folder = os.path.join(user_path, subfolders[0])
    valid_folder = os.path.join(repo_folder, ".git")
    if not os.path.exists(valid_folder):
        return None

    # Cerca il file .c dell'utente
    c_files = [f for f in os.listdir(repo_folder) if f.endswith(".c")]
    c_file_path = os.path.join(repo_folder, c_files[0]) if c_files else None

    # Parallelizza le operazioni pesanti usando un ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_commit_analysis = executor.submit(detect_large_commit_spike, valid_folder)
        future_log_analysis = executor.submit(get_average_commit_interval_from_logs, valid_folder)
        if c_file_path:
            future_code_metrics = executor.submit(detect_ai_generated_code, c_file_path)
        else:
            future_code_metrics = None

        is_large_commit_suspicious = future_commit_analysis.result()
        resultG = future_log_analysis.result()
        code_metrics = future_code_metrics.result() if future_code_metrics else {"avg_function_length": 0, "comment_ratio": 0}

    try:
        user_data = {
            "commit_count": resultG["commit_count"],
            "average_commit_interval": resultG["average_commit_interval"],
            "work_duration": resultG["total_work_duration"],
            "avg_function_length": code_metrics["avg_function_length"],
            "comment_ratio": code_metrics["comment_ratio"],
            "is_large_commit_suspicious": is_large_commit_suspicious
        }
    except Exception:
        user_data = {
            "commit_count": 0,
            "average_commit_interval": 0,
            "work_duration": 0,
            "avg_function_length": 0,
            "comment_ratio": 0,
            "is_large_commit_suspicious": False
        }

    return (user, user_data)

def get_git_analytics():
    """
    Scansiona la cartella degli utenti e raccoglie le metriche Git e del codice sorgente.
    L'elaborazione per ogni utente viene parallelizzata con un ProcessPoolExecutor,
    mentre all'interno di ogni processo, un ThreadPoolExecutor gestisce le operazioni pesanti.
    """
    analytics = {}
    commit_counts = []
    avg_intervals = []
    work_durations = []
    function_lengths = []
    comment_ratios = []

    users = os.listdir(BASE_DIR)
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(process_user, users))

    # Raccoglie i risultati validi
    for res in results:
        if res is None:
            continue
        user, user_data = res
        analytics[user] = user_data
        commit_counts.append(user_data["commit_count"])
        avg_intervals.append(user_data["average_commit_interval"])
        work_durations.append(user_data["work_duration"])
        function_lengths.append(user_data["avg_function_length"])
        comment_ratios.append(user_data["comment_ratio"])

    if len(commit_counts) < 2:
        return analytics

    global_metrics = {
        "mean_commit_count": float(np.mean(commit_counts)),
        "mean_avg_interval": float(np.mean(avg_intervals)),
        "mean_work_duration": float(np.mean(work_durations)),
        "mean_function_length": float(np.mean(function_lengths)),
        "mean_comment_ratio": float(np.mean(comment_ratios)),
        "std_commit_count": float(np.std(commit_counts)),
        "std_avg_interval": float(np.std(avg_intervals)),
        "std_work_duration": float(np.std(work_durations))
    }

    for user, data in analytics.items():
        is_suspicious = (
            abs(data["commit_count"] - global_metrics["mean_commit_count"]) > global_metrics["std_commit_count"] * 2 or
            abs(data["average_commit_interval"] - global_metrics["mean_avg_interval"]) > global_metrics["std_avg_interval"] * 2 or
            abs(data["work_duration"] - global_metrics["mean_work_duration"]) > global_metrics["std_work_duration"] * 2
        )
        analytics[user]["is_ai_generated_behavior"] = bool(is_suspicious)

    analytics["global_metrics"] = global_metrics

    return analytics


def get_users_list():
    """ Scansiona la cartella degli utenti e raccoglie le metriche Git """
    analytics = {}

    for user in os.listdir(BASE_DIR):

        analytics[user] = {
            "commit_count": 0,
            "average_commit_interval": 0,
            "work_duration": 0,
        }

    return analytics



@admin_bp.route('/api/git-analytics/<username>')
def get_user_analytics(username):
    """ Restituisce i dettagli dei commit per un singolo utente """
    user_path = os.path.join(BASE_DIR, username, "c")

    if not os.path.isdir(user_path):
        return jsonify({"error": "User not found"}), 404

    subfolders = [f for f in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, f)) and f != "sandbox"]

    if not subfolders:
        return jsonify({"error": "No valid folder found"}), 404

    repo_path = os.path.join(user_path, subfolders[0], ".git")

    if not os.path.exists(repo_path):
        return jsonify({"error": "No git repository found"}), 404

    return jsonify(get_lines_modified_per_commit(repo_path))

@admin_bp.route('/api/git-analytics')
def get_analytics():
    return jsonify(get_git_analytics())

@admin_bp.route('/api/get-users')
def get_users():
    return jsonify(get_users_list())

@admin_bp.route('/api/get-turni')
def get_turni():

    turni = model_base.getTurni()
    if(not turni):
        return jsonify([])
    turni_list = [row[0] for row in turni]
    
    return jsonify(turni_list)


@admin_bp.route('/api/get-tracce_attive')
def get_tracce_attive():

    turni = model_base.getTracceAttive()
    result = []
    for r in turni:
        temp = dict(r._mapping)
        try:
            temp['description'] = temp['description'].decode('utf-8')
            result.append(temp)

        except:
            pass
    return jsonify(result)



@admin_bp.route('/api/users_by_turno', methods=['GET'])
def users_by_turno():
    turno_id = request.args.get('turno')
    if not turno_id:
        return jsonify([])  # oppure un errore 400
    
    rows = model_base.getUsersByTurno(turno_id)
    data = []
    for r in rows:
        user_dict = {
            "matricola": r[0],
            "nome": r[1],
            "cognome": r[2],
            "assegnato": r[3]
        }
        data.append(user_dict)

    return jsonify(data), 200



@admin_bp.route('/api/users_by_turno_assigned', methods=['GET'])
def users_by_turno_assigned():
    turno_id = request.args.get('turno')
    if not turno_id:
        return jsonify([])  # oppure un errore 400
    
    rows = model_base.getUsersByTurno_AssignedOnly(turno_id)
    data = []
    if(not rows):
        return ""
    for r in rows:
        user_dict = {
            "matricola": r[0],
            "nome": r[1],
            "cognome": r[2],
            "assegnato": r[3]
        }
        data.append(user_dict)

    return jsonify(data), 200



@admin_bp.route('/charts')
def charts_page():
    return render_template('admin/charts.html')


@admin_bp.route('/admin/assign_exercises')
def assign_exercises_page():
    return render_template('admin/assign_exercise.html')

@admin_bp.route('/admin/reassign_exercises')
def reassign_exercises_page():
    return render_template('admin/re_assign_exercise.html')


@admin_bp.route('/admin/exercises')
def exercise_page():
    return render_template('admin/exercises.html')

@admin_bp.route('/api/exercises', methods=['GET'])
def get_exercises():
    """Restituisce l'elenco di tutti gli esercizi in formato JSON."""
    exercises = model_base.getAllExercices()
    # Convertiamo ciascun Exercise in dict
    result = []
    for r in exercises:
        temp = dict(r._mapping)
        try:
            temp['description'] = temp['description'].decode('utf-8')
            result.append(temp)

        except:
            pass
    return jsonify(result), 200


@admin_bp.route('/api/exercises/switchExercise', methods=['POST'])
def set_exercise_is_exam():
    """Restituisce l'elenco di tutti gli esercizi in formato JSON."""
    request_id = request.form.get('id')
    request_new_value = request.form.get('attivo')

    exercises = model_base.setExerciseActive(request_id,request_new_value )
    # Convertiamo ciascun Exercise in dict
    
    return "200"



@admin_bp.route('/user_charts')
def user_charts():
    """Mostra la pagina dei dettagli commit per un singolo utente"""
    return render_template('admin/user_charts.html')


@admin_bp.route('/admin/list_accounts', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def list_accounts():
    typ = request.args.get('all')
    if typ == 1:
        accounts = list_logged_accounts()
    else:
        accounts = list_res_accounts()

    content ="<?xml version='1.0' encoding='utf-8' ?><rows>";
    if accounts is not None:
        for account in accounts:
            content+="<row id='"+account[0]+"'><cell><![CDATA["+account[1]+"]]></cell><cell>" \
            "<![CDATA["+account[2]+"]]></cell><cell><![CDATA["+account[0]+"]]></cell><cell><![CDATA[]]></cell></row>"
        content +="</rows>"
    resp = make_response(content)
    resp.headers['Content-Type'] = 'application/xml'
    return resp

@admin_bp.route('/admin/list_prj_user', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def list_prj_user():
    accounts = list_res_accounts()
    content = "<?xml version='1.0' encoding='utf-8' ?><rows>";
    for account in accounts:
        content += "<row id='" + account[0] + "'><cell><![CDATA[]]></cell><cell>" \
                    "<![CDATA[" + account[0] + "]]></cell><cell><![CDATA[" + account[1] + "]]></cell>" \
                    "<cell><![CDATA[" + account[2] + "]]></cell><cell><![CDATA[" + str(account[4]) + "]]></cell></row>"
    content += "</rows>"
    resp = make_response(content)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@admin_bp.route('/admin/projects', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_projects():
    return render_template("admin/projects.html")


@admin_bp.route('/admin/list_projects', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_list_projects():
    projects = list_projects()
    content = "<?xml version='1.0' encoding='utf-8' ?><rows>"
    for project in projects:
        content += "<row id='"+str(project[0])+"'><cell><![CDATA["+str(project[0])+"]]></cell><cell><![CDATA["+str(project[1])+"]]></cell>" \
                   "<cell><![CDATA["+str(project[2])+"]]></cell><cell><![CDATA["+str(project[3])+"]]></cell>" \
                   "<cell><![CDATA["+str(project[4])+"]]></cell><cell><![CDATA["+str(project[2])+"]]></cell></row>"

    content += "</rows>"

    resp = make_response(content)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@admin_bp.route('/admin/settings', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_settings():
    return render_template("admin/settings.html")

@admin_bp.route('/admin/statistics', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_statistics():
    return render_template("admin/statistics.html")

@admin_bp.route('/admin/del_res_acc', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_del_res_acc():
    accounts = request.args.post('accounts')
    delete_res_accounts(accounts)
    return 0

@admin_bp.route('/admin/clearall', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def admin_clear():
    clear_session()
    return 0

@admin_bp.route('/admin/update_password', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def update_password():
    delete_all()
    return 0

@admin_bp.route('/admin/passwd_download', methods = ['GET','POST'])
@login_required
@admin_role.require(401)
def download_passwords():
    return send_file(Config.data_dir+"/passwords.csv", as_attachment=True)
 
@admin_bp.route('/admin/list_existing_shifts', methods=['GET'])
def list_existing_shifts():
    # Esempio: SELECT turno, COUNT(*) FROM reserved_users GROUP BY turno
    rows = model_base.list_by_turno()
    # rows: [(1, 10), (2, 5), ...]
    data = []
    for r in rows:
        data.append({
            "turno_id": r[0],
            "count_users": r[1]
        })
    return jsonify(data)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() ==  'csv'


@admin_bp.route('/admin/new_accounts', methods=['GET'])
@login_required
@admin_role.require(401)
def new_accounts():
    return render_template("admin/new_accounts.html")


@admin_bp.route('/admin/list_password_files', methods=['GET'])
@login_required
@admin_role.require(401)
def list_password_files():
    csv_files = []
    for filename in os.listdir(Config.data_dir):
        if filename.startswith("passwords_turno_") and filename.endswith(".csv"):
            csv_files.append(filename)
    
    return render_template("admin/list_password_files.html", csv_files=csv_files)

@admin_bp.route('/admin/download_password_file/<path:filename>', methods=['GET'])
@login_required
@admin_role.require(401)
def download_password_file(filename):
    return send_file(Config.data_dir+"/"+filename, as_attachment=True)


@admin_bp.route('/admin/upload_users', methods=['POST'])
@login_required
@admin_role.require(401)
def upload_users():
    if request.method == 'POST':
        files = request.files
        turno_files = {}  # Dizionario per associare file e turno

        for key in files:
            if key.startswith('file_'):  # Identifica i file dei turni
                turno_id = request.form.get(f'turno_id_{key.split("_")[1]}')
                file = files[key]

                if file and allowed_file(file.filename):
                    filename = secure_filename(f"turno_{turno_id}_{file.filename}")
                    file_path = os.path.join(Config.data_dir, filename)
                    file.save(file_path)
                    
                    turno_files[turno_id] = file_path

        if not turno_files:
            flash('Nessun file valido caricato.')
            return redirect(request.url)

        # Elaborazione dei file caricati
        for turno_id, file_path in turno_files.items():
            users = import_reservations(file_path)
            passwords = gen_passwords(len(users))

            # Creazione delle prenotazioni con l'ID turno
            model_base.create_reservations(np.hstack((users, passwords)), turno_id)
            model_base.create_bc_passwords(np.hstack((users[:, 0].reshape(-1, 1), passwords[:, 2].reshape(-1, 1))))
            add_atheos_users(np.hstack((users[:, 0].reshape(-1, 1), passwords[:, 2].reshape(-1, 1))),
                             Config.atheos_dir + "/data/users.json")
            csv_filename = f"passwords_turno_{turno_id}.csv"
            csv_path = os.path.join(Config.data_dir, csv_filename)
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(np.hstack((users[:, :3], passwords[:, 0].reshape(-1, 1))))

        flash('File caricati e password salvate con successo!')
        return redirect(url_for('admin_blueprint.list_password_files'))

    return 0



@admin_bp.route('/admin/change_password', methods=['POST'])
@login_required
def change_password():
        serial_number = request.form.get('serialNumber')
        new_password = request.form.get('password')
        if not serial_number or not new_password:
            return "Dati mancanti", 400

        # Genera l'hash come in gen_passwords
        # 1) SHA-256
        sha_hash, bc_hash = hash_password(new_password)
        model_base.update_password(serial_number, sha_hash, bc_hash)
        update_atheos_user(serial_number, bc_hash)
        return "ok", 200





@admin_bp.route('/admin/delete_users', methods=['POST'])
@login_required
def delete_user():
        import json
        users = json.loads(request.form.get('utenti'))
        for(user) in users:
            model_base.delete_single_res_accounts(user)
            delete_user_dirs(user)
            delete_atheos_user(user)
            delete_atheos_projects(user)
        return "ok", 200



@admin_bp.route('/api/modifica_assegnazione', methods = ['POST'])
@login_required
@admin_role.require(401)
def modifica_assegnazione():
    import json
    users = json.loads(request.form.get('utenti'))
    tracce_json = request.form.get('tracce')
    rand = request.form.get('random')
    lang =request.form.get('lang')
    test_name = request.form.get('test_name')
    desc = request.form.get('description')

    if desc is None:
        desc = ""
    
    exercises = model_base.getexercises(isexam=1,  lang=lang)
    exercise_ids = [exercise[0] for exercise in exercises]
    print(len(users), exercise_ids)
    for user in users:
        delete_user_dirs(user)
    if rand:
        projects = create_random_projects(len(users),exercise_ids)
        users_new = np.hstack((np.array(users).reshape(-1,1),np.array(projects).reshape(-1,1)))
      
        model_base.update_projects(users_new, lang)
        prj_dirs = []
        for project in projects:
            prj_dirs.append(model_base.getexercisefolder(project, isexam=1)[0])
        user_projects = np.hstack((users_new[:,0].reshape(-1,1),np.array(prj_dirs).reshape(-1,1)))
        create_prj_dirs(Config.data_dir, Config.users_dir, user_projects)
        update_atheos_projects(user_projects, Config.atheos_dir+"/data/projects.db.json", Config.users_dir)
        restrict_atheos_acl(Config.atheos_dir+"/data/users.json",user_projects,Config.users_dir)
        model_base.setUsersAsAssigned(users)
    return ""





@admin_bp.route('/api/create_projects', methods = ['POST'])
@login_required
@admin_role.require(401)
def create_projects():
    import json
    users = json.loads(request.form.get('utenti'))
    tracce_json = request.form.get('tracce')
    rand = request.form.get('random')
    lang =request.form.get('lang')
    test_name = request.form.get('test_name')
    desc = request.form.get('description')

    if desc is None:
        desc = ""
    
    exercises = model_base.getexercises(isexam=1,  lang=lang)
    exercise_ids = [exercise[0] for exercise in exercises]
    print(len(users), exercise_ids)
    
    if rand:
        projects = create_random_projects(len(users),exercise_ids)
        users_new = np.hstack((np.array(users).reshape(-1,1),np.array(projects).reshape(-1,1)))
      
        model_base.create_projects(users_new, lang)
        prj_dirs = []
        for project in projects:
            prj_dirs.append(model_base.getexercisefolder(project, isexam=1)[0])
        user_projects = np.hstack((users_new[:,0].reshape(-1,1),np.array(prj_dirs).reshape(-1,1)))
        create_prj_dirs(Config.data_dir, Config.users_dir, user_projects)
        update_atheos_projects(user_projects, Config.atheos_dir+"/data/projects.db.json", Config.users_dir)
        restrict_atheos_acl(Config.atheos_dir+"/data/users.json",user_projects,Config.users_dir)
        model_base.setUsersAsAssigned(users)
    return ""


@admin_bp.route('/admin/update_project', methods = ['POST'])
@login_required
@admin_role.require(401)
def update_project():
      
    prj_id = request.form.get('id')
    exercise = request.form.get('exercise')
    users = [request.form.get('user')]
    project = model_base.getproject(users[0])
   
    prj_folder = model_base.getexercisefolder(project['exercise'], isexam=1)[0]
   
    delete_prj_dirs(Config.data_dir, Config.users_dir, [[users[0], prj_folder]])
    model_base.delete_projects([int(prj_id)])
    projects = create_random_projects(len(users),[int(exercise)])
    users = np.hstack((np.array(users).reshape(-1,1),np.array(projects).reshape(-1,1))) 
    model_base.create_projects(users, 'c', 'updated', 'updated')
    prj_dirs = []
    prj_dirs.append(model_base.getexercisefolder(projects[0], isexam=1)[0])
    user_projects = np.hstack((users[:,0].reshape(-1,1),np.array(prj_dirs).reshape(-1,1)))
    create_prj_dirs(Config.data_dir, Config.users_dir, user_projects)
    update_atheos_projects(user_projects, Config.atheos_dir+"/data/projects.db.json", Config.users_dir)
    restrict_atheos_acl(Config.atheos_dir+"/data/users.json",user_projects,Config.users_dir)
    
    return "1"

@admin_bp.route('/admin/exercise_list', methods = ['GET'])
@login_required
@admin_role.require(401)
def exercise_list():
    exercises = model_base.getexercises('c', 1)
    exercise_ids = [exercise[0] for exercise in exercises]
    return   exercise_ids



@admin_bp.route('/admin/clear_session', methods = ['GET'])
@login_required
@admin_role.require(401)
def clear_session():
    os.system("sh /home/evaluatex/data/restore.sh")

    model_base.clear_session()
    return ("", 204)