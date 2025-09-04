"""
Instructions for using this script
1. Create a csv containing the information on all repositories you with to generate log files for. This csv
   must have two columns, Organization and Repository. Organization should be the GitHub organization that owns the
   repository and Repository should be the repository name. An example csv for the repositories
   https://github.com/django/django-asv and https://github.com/django/code-of-conduct would be:
   Organization | Repository
   django, django-asv
   django, code-of-conduct
2. If you have not already, set up GitHub authentication on your computer. Instructions can be found here:
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

GIT_LOG_COMMAND = f"git log --remotes --pretty=medium --no-color --date=default --stat --after='{year - 1}-12-31' --before='{year + 1}-01-01'"
GIT_LOG_COMMAND_SPLIT = GIT_LOG_COMMAND.split(" ")

os.makedirs(f"{os.getcwd()}/git_log_files", exist_ok=True)

with open(repos_csv_path) as repos_file:
    reader = csv.DictReader(repos_file)
    for row in reader:
        org_name = row["Organization"].lower().strip()
        repo_name = row["Repository"].lower().strip()
        print(f"Processing {org_name}/{repo_name}")
        # Clone repo
        subprocess.run(["git", "clone", f"https://github.com/{org_name}/{repo_name}.git"])
        # Change to newly cloned repo
        os.chdir(repo_name)
        # Generate the git log file and save it
        output_file_path = f"../git_log_files/{repo_name}_git_log_{year}_01_01-{year}_12_31.txt"
        with open(output_file_path, "w") as output_file:
            subprocess.run(GIT_LOG_COMMAND_SPLIT, stdout=output_file)
        # Change back to parent directory
        os.chdir("..")
        # Delete the cloned repo
        subprocess.run(["rm", "-rf", repo_name])

