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

