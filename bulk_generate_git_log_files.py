import os
import csv
import sys
import subprocess



LOCAL_OUTPUT_DIRECTORY = os.path.join("/Users" ,"theoyannekis", "Desktop", "temp_dir")

os.makedirs(LOCAL_OUTPUT_DIRECTORY, exist_ok=True)


if len(sys.argv) != 3:
    raise ValueError("Missing command line arguments. Both year and repository name file path must be provided")
year_str = sys.argv[1]
repos_csv_path = sys.argv[2]

# Parse the year
try:
    year = int(year_str)
except ValueError:
    raise ValueError("Invalid year given")

GIT_LOG_COMMAND = f"git log --remotes --pretty=medium --no-color --date=default --stat --after='{year - 1}-12-31' --before='{year + 1}-01-01'"

# TODO: validation of input

# TODO: temporarily clone the repo

with open(repos_csv_path) as repos_file:
    reader = csv.DictReader(repos_file)
    for row in reader:
        org_name = row["Organization"].lower().strip()
        repo_name = row["Repository"].lower().strip()
        print(f"Processing {org_name}/{repo_name}")
        # TODO: clone and move into the correct repo
        output_file_path = f"{repo_name}_git_log_{year}_01_01-{year}_12_31.txt"
        with open(output_file_path, "w") as output_file:
            subprocess.run(GIT_LOG_COMMAND.split(" "), stdout=output_file)

#
# with open(LOCAL_OUTPUT_FILE, mode="w", encoding="utf-8") as csvfile:
#
#
# local_output_file = os.path.join(LOCAL_OUTPUT_DIRECTORY, f"azure_devops_{repository_name}_pull_requests.csv")
#
