pipeline {
    agent any

    environment {
        PYTHON_PATH = 'python'  // Windows typically has python in PATH
        BITBUCKET_CREDS = credentials('d68eb646-f561-4194-a5be-a369c2f86120')
        REPO_OWNER = 'sinisterlab'
    }

    stages {
        stage('Run Stale Branch Cleanup for Selected Repos') {
            steps {
                script {
                    powershell '''
                    Write-Host "Running stale branch cleanup on selected repositories under $env:REPO_OWNER..."

                    @"
import os
import requests
from datetime import datetime, timedelta, timezone

USERNAME = os.getenv('USERNAME')
APP_PASSWORD = os.getenv('APP_PASSWORD')
REPO_OWNER = os.getenv('REPO_OWNER')

REPO_SLUGS = [
    'adv-app',
]

PROTECTED_BRANCHES = ['main']
CUTOFF_DAYS = 1
DRY_RUN = True
cutoff_date = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)

global_total_checked = 0
global_stale_found = 0
global_deleted = 0

def clean_branches(repo_slug):
    global global_total_checked, global_stale_found, global_deleted

    print(f"Cleaning branches for repo: {repo_slug}")
    base_url = f"https://api.bitbucket.org/2.0/repositories/{REPO_OWNER}/{repo_slug}/refs/branches"
    url = base_url
    visited_urls = set()
    branches_to_delete = []
    total_branches_checked = 0

    while url:
        if url in visited_urls:
            print(f"Repeated URL detected, breaking loop: {url}")
            break
        visited_urls.add(url)

        try:
            resp = requests.get(url, auth=(USERNAME, APP_PASSWORD), timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Error fetching branches for {repo_slug}: {e}")
            break

        for branch in data.get('values', []):
            total_branches_checked += 1
            name = branch['name']
            date_str = branch['target']['date']
            last_commit = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
            if name not in PROTECTED_BRANCHES and last_commit < cutoff_date:
                branches_to_delete.append((name, last_commit.isoformat()))

        url = data.get("next")

    global_total_checked += total_branches_checked
    global_stale_found += len(branches_to_delete)

    print(f"Checked {total_branches_checked} branches in {repo_slug}. Found {len(branches_to_delete)} stale branches.")

    for name, date in branches_to_delete:
        if DRY_RUN:
            print(f"[DRY RUN] Would delete: {name} (last commit: {date})")
        else:
            del_url = f"{base_url}/{name}"
            response = requests.delete(del_url, auth=(USERNAME, APP_PASSWORD))
            if response.status_code == 204:
                print(f"Deleted: {name}")
                global_deleted += 1
            else:
                print(f"Failed to delete {name}: {response.status_code} - {response.text}")

def main():
    if not USERNAME or not APP_PASSWORD or not REPO_OWNER:
        print("Missing environment variables.")
        return

    print(f"Repositories selected: {len(REPO_SLUGS)}")
    for repo_slug in REPO_SLUGS:
        clean_branches(repo_slug)

    print("\\n====== Final Summary ======")
    print(f"Total repositories scanned: {len(REPO_SLUGS)}")
    print(f"Total branches checked:     {global_total_checked}")
    print(f"Stale branches found:       {global_stale_found}")
    print(f"Deleted branches:            {global_deleted if not DRY_RUN else 0}")
    print(f"Dry run mode:               {'ON' if DRY_RUN else 'OFF'}")
    print("================================\\n")

if __name__ == "__main__":
    main()
"@ | Out-File -FilePath "cleanup_selected_repos.py" -Encoding UTF8

                    $env:USERNAME = "$env:BITBUCKET_CREDS_USR"
                    $env:APP_PASSWORD = "$env:BITBUCKET_CREDS_PSW"
                    $env:REPO_OWNER = "$env:REPO_OWNER"

                    & $env:PYTHON_PATH cleanup_selected_repos.py
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Cleanup completed across selected repos.'
        }
        failure {
            echo 'Cleanup failed.'
        }
    }
}
