import os
import sys
import requests
from datetime import datetime, timedelta, timezone

# Configuration
USERNAME = os.environ.get('BITBUCKET_USERNAME')
APP_PASSWORD = os.environ.get('BITBUCKET_APP_PASSWORD')
REPO_OWNER = 'sinisterlab'
REPO_SLUGS = ['adv-app']
PROTECTED_BRANCHES = ['main']
CUTOFF_DAYS = 0  # Set to desired number of days
cutoff_date = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
today_str = datetime.now().strftime('%Y%m%d')

# Summary counters
global_total_checked = 0
global_stale_found = 0
global_deleted = 0

# Read dry run flag from CLI args
DRY_RUN = True
if len(sys.argv) > 1:
    DRY_RUN = sys.argv[1].lower() == 'true'


def add_dummy_file_commit(repo_slug, branch_name):
    print(f"Adding dummy commit to branch {branch_name}")
    url = f"https://api.bitbucket.org/2.0/repositories/{REPO_OWNER}/{repo_slug}/src"
    try:
        response = requests.post(
            url,
            auth=(USERNAME, APP_PASSWORD),
            files={
                'branch': (None, branch_name),
                'message': (None, f'Add dummy .backup_marker on {datetime.now().isoformat()}'),
                'files': ('.backup_marker', f'Backup created on {datetime.now().isoformat()}'),
            }
        )
        if response.status_code in [200, 201]:
            print(f"Dummy commit added to {branch_name}")
        else:
            print(f"Failed to add dummy commit: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error adding dummy commit to {branch_name}: {e}")


def backup_protected_branch(repo_slug, branch_name):
    backup_branch = f"{branch_name}_backup_{today_str}"
    base_url = f"https://api.bitbucket.org/2.0/repositories/{REPO_OWNER}/{repo_slug}"
    get_branch_url = f"{base_url}/refs/branches/{branch_name}"
    backup_url = f"{base_url}/refs/branches/{backup_branch}"
    create_branch_url = f"{base_url}/refs/branches"

    print(f"\nEnsuring latest backup for: {branch_name} --> {backup_branch}")

    try:
        # Delete existing backup with same name if exists
        check_resp = requests.get(backup_url, auth=(USERNAME, APP_PASSWORD))
        if check_resp.status_code == 200:
            if not DRY_RUN:
                del_resp = requests.delete(backup_url, auth=(USERNAME, APP_PASSWORD))
                if del_resp.status_code == 204:
                    print(f"Deleted existing backup branch: {backup_branch}")
                else:
                    print(f"Failed to delete old backup: {backup_branch} - {del_resp.status_code} - {del_resp.text}")
            else:
                print(f"[DRY RUN] Would delete existing backup: {backup_branch}")

        # Get latest commit hash of original branch
        resp = requests.get(get_branch_url, auth=(USERNAME, APP_PASSWORD))
        resp.raise_for_status()
        commit_hash = resp.json()['target']['hash']

        if DRY_RUN:
            print(f"[DRY RUN] Would create backup: {backup_branch} from {branch_name} @ {commit_hash}")
            return

        # Create new backup branch
        payload = {
            "name": backup_branch,
            "target": {"hash": commit_hash}
        }
        create_resp = requests.post(create_branch_url, auth=(USERNAME, APP_PASSWORD), json=payload)

        if create_resp.status_code == 201:
            print(f"Backup created: {backup_branch}")
            add_dummy_file_commit(repo_slug, backup_branch)
        else:
            print(f"Failed to create backup for {branch_name}: {create_resp.status_code} - {create_resp.text}")

    except Exception as e:
        print(f"Error backing up {branch_name}: {e}")


def clean_branches(repo_slug):
    global global_total_checked, global_stale_found, global_deleted

    print(f"\nCleaning branches for repo: {repo_slug}")
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
             if (
               name not in PROTECTED_BRANCHES
               and last_commit < cutoff_date
            ):
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
    if not USERNAME or not APP_PASSWORD:
        print("Error: Missing BITBUCKET_USERNAME or BITBUCKET_APP_PASSWORD environment variables.")
        return

    print(f"Repositories selected: {len(REPO_SLUGS)}")
    print(f"Dry run mode: {'ON' if DRY_RUN else 'OFF'}")

    for repo_slug in REPO_SLUGS:
        for branch in PROTECTED_BRANCHES:
            backup_protected_branch(repo_slug, branch)

    for repo_slug in REPO_SLUGS:
        clean_branches(repo_slug)

    print("\n====== Final Summary ======")
    print(f"Total repositories scanned: {len(REPO_SLUGS)}")
    print(f"Total branches checked:     {global_total_checked}")
    print(f"Stale branches found:       {global_stale_found}")
    print(f"Deleted branches:           {global_deleted if not DRY_RUN else 0}")
    print("================================\n")


if __name__ == "__main__":
    main()
