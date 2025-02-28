import os
import git
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_diff_lines(repo, commit, filename):
    # Ottieni il diff tra il commit corrente e il commit precedente
    diff_text = repo.git.diff(f'{commit.hexsha}~1..{commit.hexsha}', filename)

    # Conta il numero di righe aggiunte e rimosse nel diff
    lines_added = sum(1 for line in diff_text.split('\n') if line.startswith('+') and not line.startswith('+++'))
    lines_removed = sum(1 for line in diff_text.split('\n') if line.startswith('-') and not line.startswith('---'))

    return lines_added + lines_removed


def get_commit_info(repo, filename, date_string):
    commit_info = []
    i = 0
    date_format = "%Y-%m-%d %H:%M:%S"

    # Convert the string to a datetime object
    date_object = datetime.strptime(date_string, date_format)

    for commit in repo.iter_commits(paths=filename):
        
        if (datetime.utcfromtimestamp(commit.committed_date) > date_object ):
            commit_info.append({
                'date': datetime.utcfromtimestamp(commit.committed_date),
                'lines': sum(1 for line in repo.git.show(f'{commit.hexsha}:{filename}').split('\n')),
                'lines_changed': get_diff_lines(repo, commit, filename)
            })
    return sorted(commit_info, key=lambda x: x['date'])  # Ordina per data crescente

def plot_chart(commit_info, repo_name):
    dates = [info['date'] for info in commit_info]
    lines = [info['lines'] for info in commit_info]
    plt.plot(dates, lines, marker='o', label=f'Repo {repo_name}')


def plot2_chart(commit_info, repo_name):
    dates = [info['date'] for info in commit_info]
    lines = [info['lines_changed'] for info in commit_info]
    plt.plot(dates, lines, marker='o', label=f'Repo {repo_name}')

def main(date_string):
    users_path = './users'
    c_subfolder = 'c'

    for user_folder in os.listdir(users_path):
        user_path = os.path.join(users_path, user_folder)

        # Trova tutte le sottocartelle 'c' eccetto 'sandbox'
        c_folders = [c_folder for c_folder in os.listdir(os.path.join(user_path, c_subfolder)) if c_folder != 'sandbox']

        for repo_name in c_folders:
            repo_path = os.path.join(user_path, c_subfolder, repo_name)
            filename = 'main.c'

            if not os.path.exists(repo_path):
                print(f"Error: Repository not found at {repo_path}")
                return

            repo = git.Repo(repo_path)
            commit_info = get_commit_info(repo, filename, date_string)
            plot2_chart(commit_info, user_folder)

    ax = plt.gca()
    xfmt = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    plt.xlabel('Commit Time')
    plt.ylabel('Number of Lines')
    plt.title('Number of Lines in main.c Over Time')
    plt.legend(title='Repositories', markerscale=0.5, title_fontsize='15', fontsize='10', loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    date_string = "2024-01-24 00:30:00"

    main(date_string)
