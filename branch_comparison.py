import requests
import os
import sys
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

# Bitbucket API configura`tion
BASE_URL = "https://api.bitbucket.org/2.0"
USERNAME = os.environ.get("BITBUCKET_USERNAME")
APP_PASSWORD = os.environ.get("BITBUCKET_PASSWORD")
WORKSPACE = os.environ.get("WORKSPACE")
SOURCE_BRANCH = os.environ.get("SOURCE_BRANCH")
DESTINATION_BRANCH = os.environ.get("DESTINATION_BRANCH")

print(f"Using username: {USERNAME}")
print(f"Password length: {'*' * len(APP_PASSWORD) if APP_PASSWORD else 'No password provided'}")
print(f"Workspace: {WORKSPACE}")

# List of repositories to exclude from checking
EXCLUDED_REPOS = [
    "dokerautopilot"
    # Add more as needed
]

def get_repositories(auth, workspace):
    """Get all repositories in the workspace"""
    repositories = []
    url = f"{BASE_URL}/repositories/{workspace}"
    next_url = url
    print(f"Fetching repositories from workspace '{workspace}'...")

    while next_url:
        response = requests.get(next_url, auth=auth)

        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            print(response.text)
            return []

        data = response.json()
        repositories.extend(data.get('values', []))

        # Get next page if it exists
        next_url = data.get('next')

    # Filter out excluded repositories
    filtered_repos = [repo for repo in repositories if repo['slug'] not in EXCLUDED_REPOS]

    print(f"Found {len(repositories)} repositories.")
    print(f"Excluded {len(repositories) - len(filtered_repos)} repositories from checking.")
    print(f"Will check {len(filtered_repos)} repositories.")

    return filtered_repos


def check_branch_exists(auth, workspace, repo_slug, branch_name):
    """Check if a branch exists in the repository"""
    url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/refs/branches/{quote(branch_name)}"
    response = requests.get(url, auth=auth)
    return response.status_code == 200


def find_default_branch(auth, workspace, repo_slug, preferred_branches=["master", "main"]):
    """Try to find a default branch from the list of preferred branches"""
    for branch in preferred_branches:
        if check_branch_exists(auth, workspace, repo_slug, branch):
            return branch
    return None


def compare_branches(auth, workspace, repo_slug, source, destination):
    """Compare two branches and get the commit differences"""
    # First check if source branch exists
    if not check_branch_exists(auth, workspace, repo_slug, source):
        return {"error": f"Source branch '{source}' does not exist"}

    # Check if destination branch exists, if not try fallbacks
    if not check_branch_exists(auth, workspace, repo_slug, destination):
        # Try to find a default branch
        default_branch = find_default_branch(auth, workspace, repo_slug)
        if default_branch:
            print(f"Note: Using '{default_branch}' instead of '{destination}' for {repo_slug}")
            destination = default_branch
        else:
            return {"error": f"Neither '{destination}', 'master', nor 'main' branch exists"}

    # URL encode branch names
    source_encoded = quote(source)
    dest_encoded = quote(destination)

    url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/commits"
    params = {
        'include': source_encoded,
        'exclude': dest_encoded
    }

    response = requests.get(url, auth=auth, params=params)

    if response.status_code != 200:
        return {"error": f"Error comparing branches: {response.status_code} - {response.text}"}

    commits = response.json().get('values', [])
    return {"commits": commits, "actual_destination": destination}


def check_repository(auth, workspace, repo, source, destination):
    """Check a single repository for changes between branches"""
    repo_slug = repo['slug']
    repo_name = repo['name']

    result = compare_branches(auth, workspace, repo_slug, source, destination)

    if "error" in result:
        return {
            "repo_slug": repo_slug,
            "repo_name": repo_name,
            "status": "error",
            "message": result["error"],
            "commits": []
        }

    commits = result["commits"]
    actual_destination = result.get("actual_destination", destination)

    return {
        "repo_slug": repo_slug,
        "repo_name": repo_name,
        "status": "success",
        "has_changes": len(commits) > 0,
        "commits": commits,
        "actual_destination": actual_destination
    }


def display_repository_results(results, source, requested_destination):
    """Display the results of repository checks"""
    repos_with_changes = []
    repos_with_errors = []
    repos_without_changes = []
    repos_with_alt_branch = []

    for result in results:
        if result["status"] == "error":
            repos_with_errors.append(result)
        else:
            # Check if an alternative destination branch was used
            actual_dest = result.get("actual_destination", requested_destination)
            if actual_dest != requested_destination:
                repos_with_alt_branch.append((result, actual_dest))

            if result["has_changes"]:
                repos_with_changes.append(result)
            else:
                repos_without_changes.append(result)

    # Display repositories with changes
    if repos_with_changes:
        print("REPOSITORIES WITH CHANGES")
        for repo in repos_with_changes:
            print(f"Repository: {repo['repo_name']} ({repo['repo_slug']})")
            actual_dest = repo.get("actual_destination", requested_destination)
            if actual_dest != requested_destination:
                print(f"   Using branch: {actual_dest} (fallback from {requested_destination})")
            print(f"   Found {len(repo['commits'])} commits to merge from {source} to {actual_dest}")

            # Display first 3 commits for each repo with changes
            for i, commit in enumerate(repo['commits'][:3], 1):
                print(f"   - Commit {i}: {commit['message'].strip()[:60]}")

            if len(repo['commits']) > 3:
                print(f"   - ... and {len(repo['commits']) - 3} more commits")

    # Display repositories with errors
    if repos_with_errors:
        print("REPOSITORIES WITH ERRORS")
        for repo in repos_with_errors:
            print(f"Error: {repo['repo_name']} ({repo['repo_slug']}): {repo['message']}")
    
    # Summary section will be used for Jenkins build description
    print("SUMMARY")
    summary_lines = [
    f"Total repositories checked: {len(results)}",
    f"Repositories with changes: {len(repos_with_changes)}"
    ]
    if repos_with_changes:
        summary_lines.append("  - " + "\n  - ".join([f"{repo['repo_name']} ({repo['repo_slug']})" for repo in repos_with_changes]))

    summary_lines.append(f"Repositories with errors: {len(repos_with_errors)}")
    if repos_with_errors:
        summary_lines.append("  - " + "\n  - ".join([f"{repo['repo_name']} ({repo['repo_slug']})" for repo in repos_with_errors]))

    summary_lines.append(f"Repositories with fallback branch: {len(repos_with_alt_branch)}")
    if repos_with_alt_branch:
        summary_lines.append("  - " + "\n  - ".join([f"{repo[0]['repo_name']} ({repo[0]['repo_slug']}) used {repo[1]}" for repo in repos_with_alt_branch]))

    summary_lines.append(f"Repositories without changes: {len(repos_without_changes)}")
    if repos_without_changes:
        summary_lines.append("  - " + "\n  - ".join([f"{repo['repo_name']} ({repo['repo_slug']})" for repo in repos_without_changes]))

    summary = "\\n".join(summary_lines)


    print(summary)
    
    # Write summary to a file for Jenkins to use
    with open('branch_comparison_summary.txt', 'w') as f:
        f.write(summary)
        
        # Also write detailed results for repositories with changes
        if repos_with_changes:
            f.write("\n\nRepositories needing attention:\n")
            for repo in repos_with_changes:
                actual_dest = repo.get("actual_destination", requested_destination)
                branch_info = f"{source} -> {actual_dest}"
                f.write(f"- {repo['repo_name']} ({repo['repo_slug']}): {len(repo['commits'])} commits ({branch_info})\n")


def main():
    """Main entry point for the script"""
    auth = (USERNAME, APP_PASSWORD)
    repos = get_repositories(auth, WORKSPACE)

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_repo = {executor.submit(check_repository, auth, WORKSPACE, repo, SOURCE_BRANCH, DESTINATION_BRANCH): repo for repo in repos}
        for future in future_to_repo:
            result = future.result()
            results.append(result)

    display_repository_results(results, SOURCE_BRANCH, DESTINATION_BRANCH)

if __name__ == "__main__":
    main()