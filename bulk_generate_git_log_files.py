"""
Instructions for generating Git logs from repositories hosted anywhere
1. Create a CSV containing a list of all repositories you with to generate log files for. This CSV
   must have three column headers: GitHub Org, GitHub Repository, and Non-GitHub Git clone URL.
   For repos on GitHub, fill in only the first two columns; for repos on other Git hosting
   platforms like GitLab and Azure DevOps, fill in only the third column.
   For example, for the GitHub repository https://github.com/django/django-asv, the GitHub Org is
   "django", and the GitHub Repository is "django-asv".
2. If you're downloading repos from GitHub, set up GitHub authentication on your computer.
   Instructions can be found here:
   https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git
3. Open a terminal, navigate to the directory containing this script, and run it as follows:
   python bulk_generate_git_log_files.py {year} {path_to_repository_csv}
   If you want commits from 2024 and the path to the repository information csv is "repo_names.csv" the command
   would be python bulk_generate_git_log_files.py 2024 repo_names.csv
"""
import os
import csv
import sys
import subprocess

# Parse command line arguments
if len(sys.argv) != 3:
    raise ValueError("Missing command line arguments. Both year and repository info file path must be provided")
year_str = sys.argv[1]
repos_csv_path = sys.argv[2]

try:
    year = int(year_str)
except ValueError:
    raise ValueError("Invalid year given")

GIT_LOG_COMMAND = f"git log --all --pretty=medium --no-color --date=default --stat --after='{year - 1}-12-31' --before='{year + 1}-01-01'"
GIT_LOG_COMMAND_SPLIT = GIT_LOG_COMMAND.split(" ")

os.makedirs(f"{os.getcwd()}/git_log_files", exist_ok=True)

with open(repos_csv_path) as repos_file:
    reader = csv.DictReader(repos_file)
    for row in reader:
        org_name = row["GitHub Org"].strip()
        repo_name = row["GitHub Repository"].lower().strip()
        clone_url = row["Non-GitHub Git clone URL"].strip()

        # Handle a GitHub repo
        if org_name != "" and repo_name != "":
            print(f"\nAttempting to download {org_name}/{repo_name} from GitHub")
            clone_url = f"git@github.com:{org_name}/{repo_name}.git"

        # Handle a repo hosted not on GitHub (e.g. on GitLab or Azure DevOps)
        elif clone_url != "":
            print(f"\nAttempting to download {clone_url}")
            repo_name = clone_url.split("/")[-1].split(".git")[0]
            print(f"repo_name = {repo_name}")

        folder_name = repo_name + ".git"
        # Clone repo
        subprocess.run(["git", "clone", "--bare", clone_url])
        # Change to newly cloned repo
        os.chdir(folder_name)
        # Generate the git log file and save it
        output_file_path = f"../git_log_files/{repo_name}_git_log_{year}_01_01-{year}_12_31.txt"
        with open(output_file_path, "w") as output_file:
            subprocess.run(GIT_LOG_COMMAND_SPLIT, stdout=output_file)
        # Change back to parent directory
        os.chdir("..")
        # Delete the cloned repo
        subprocess.run(["rm", "-rf", folder_name])
