import json
# from app.config import Config
from werkzeug.security import generate_password_hash
import re
import random
import numpy as np
import os
import shutil
import subprocess
import glob

# from app.models.base import create_reservations



def clean_string(s):
    s.replace(" ","_")
    s = re.sub("[!#$%^&*()[]{};:./<>?\|`~-=+]", "", s)
    return s

def new_password(pass_len):
  charset = '0123456789abcdefghijklmnopqrstuvwxyz'
  charset_len = len(charset)
  randomString = ''
  for i in range(pass_len):
    randomString += charset[random.randint(0, charset_len - 1)]
  return randomString

def import_reservations(filename):
    with  open(filename,"r") as fin:
        users = None
        lines = fin.readlines()
        users_started = False
        for line in lines:
            if not users_started:
                if line[0]=="#":
                    users_started = True
                continue
            else:
                line = clean_string(line)
                line = line.split(",")
                user = line[2:5]
                if line[13][-1]  =="\n":
                    line[13]=line[13][:-1]    
                user.append(line[13])
                user[0] = user[0].lower()
                if users is None:
                    users = [user]
                else:
                    users = np.vstack((users,user))
        return users
    





def add_atheos_users(users, users_file):
    user_template = '{"resetPassword": false, "creationDate": "2023-07-12 23:10:23", \
                     "activeProject": "", "lastLogin": "2023-09-08 03:02:22", \
                     "permissions": ["read", "write"]}' 
    fin = open(users_file, "r")

    jsobj = json.load(fin)
    fin.close()
    keys = jsobj.keys()
    for user in users:
        jsobj[user[0]]= json.loads(user_template)
        jsobj[user[0]]["password"] = user[1]
        jsobj[user[0]]["activeName"] = user[0]
        jsobj[user[0]]["userACL"] =  ["/home/evaluatex/users/"+user[0]+"/c/traccia"]
        jsobj[user[0]]["activePath"] = "/home/evaluatex/users/"+user[0]+"/c/traccia"
    with open(users_file, "w") as fout:
        json.dump(jsobj,fout, indent=4)


def gen_passwords(n_pass):
    passwords = None
    for i in range(n_pass):
        password = new_password(10)
        sha_hash = generate_password_hash(password,"sha256")
        # converting password to array of bytes
        bytes = password.encode('utf-8')
        # generating the salt
        import bcrypt
        salt = bcrypt.gensalt()
        # Hashing the password
        bc_hash = bcrypt.hashpw(bytes, salt)
        if passwords is None:
            passwords = [password, sha_hash, bc_hash]
        else:
            passwords = np.vstack((passwords,[password, sha_hash, bc_hash.decode()]))
       
    return passwords
        


def update_atheos_projects(users, projects_file, prj_dir):
    fin = open(projects_file, "r")
    jsobj = json.load(fin)
    fin.close()
    keys = jsobj.keys()
    for user in users:
        #if user[0] in keys:
        #    continue
        jsobj[user[0]]= prj_dir+"/"+user[0]+"/"+user[1]
    fout = open(projects_file, "w")
    json.dump(jsobj, fout,indent=4)  

def restrict_atheos_acl(users_file, users, proj_dir):
    fin = open(users_file, "r")

    jsobj = json.load(fin)
    fin.close()
    keys = jsobj.keys()
    for user in users:
        if user[0]in keys:
            jsobj[user[0]]["userACL"]= [proj_dir+"/"+user[0]+"/"+user[1]]
            jsobj[user[0]]["activePath"] = proj_dir+"/"+user[0]+"/"+user[1]
    with open(users_file, "w") as fout:
        json.dump(jsobj,fout, indent=4)

def create_random_projects(n_users, test_ids):
    user_tests  = []
    assigned = np.zeros(len(test_ids))
    avg_test = n_users/len(test_ids)
    for i in range(n_users):
        exercise = random.randint(0, len(test_ids)-1)
        while assigned[exercise] > avg_test:
            exercise = random.randint(0, len(test_ids)-1)
        assigned[exercise] += 1
        user_tests.append(test_ids[exercise])

    return user_tests
       
def delete_prj_dirs(data_dir, users_dir, projects):
    for project in projects:
        prj_dir = users_dir+"/"+project[0]+"/"+project[1]  
        if os.path.isdir(prj_dir):
            shutil.rmtree(prj_dir)

def create_prj_dirs(data_dir, users_dir, projects):
    for project in projects:
        prj_dir = users_dir+"/"+project[0]+"/"+project[1]
        print(prj_dir, data_dir+"/exercises/"+project[1]+"/template/*")
    
        if not os.path.isdir(prj_dir):
            os.makedirs(prj_dir)
            for file in glob.glob(data_dir+"/exercises/"+project[1]+"/template/*"):
                shutil.copy(file, prj_dir)
            cmd_array = ["chown", "-R","www-data:www-data", prj_dir]
            cprocess = subprocess.run(cmd_array, cwd=prj_dir)
            cmd_array = ["git", "config", "--global", "--add", "safe.directory", prj_dir]
            cprocess = subprocess.run(cmd_array, cwd=prj_dir)
            cmd_array = ["git", "init"]
            cprocess = subprocess.run(cmd_array, cwd=prj_dir)
            cmd_array = ["git", "add", "*"]
            cprocess = subprocess.run(cmd_array, cwd=prj_dir)
            cmd_array = ["git", "commit", "-m", "create_project"]
            cprocess = subprocess.run(cmd_array, cwd=prj_dir)
    
    


if __name__ == "__main__":
    users_file = "/var/www/html/data/users.json"
    users_file = "users.json"
    projects_file = "../../atheos_module/data/projects.db.json"


    # add_atheos_users([("prova", "$2y$10$BYyH.PV7hASoLeE4aKZTJOH47iXHcwWo64vx7DyFbLbfU2R3KjTK6"), ("prova2", "$2y$10$BYyH.PV7hASoLeE4aKZTJOH47iXHcwWo64vx7DyFbLbfU2R3KjTK6")])
    users = import_reservations("/data/didattica/esami/elprog/20230913/prenotati.csv")
    # print(users[:,:3])
    
    passwords = gen_passwords(len(users))
    # full_users = np.hstack((users[:,0].reshape(-1,1),passwords[:,0].reshape(-1,1)))
    # print(full_users[0,1])
    add_atheos_users(np.hstack((users[:,0].reshape(-1,1),passwords[:,0].reshape(-1,1))),users_file)
