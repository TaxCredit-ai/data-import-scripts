# This script downloads Merge Requests and their comments (called "Notes") from
# a repository hosted on GitLab.

import requests
import csv

# CONFIGURATION AND SETUP:
# Customize this to wherever your GitLab repo is hosted, e.g.
# "https://gitlab.com" or  "https://gitlab.mycompany.com"
GITLAB_URL = "https://gitlab.com"
# Create a Personal Access Token with the "read_api" permission scope
PERSONAL_ACCESS_TOKEN = "..."
# The project/repository ID from the top of the main page of the repository
# (more info here: https://stackoverflow.com/a/53126068/1789466)
REPO_ID = 1234567
# The full path of the local file you want the output written to
LOCAL_OUTPUT_FILE = "/home/myusername/Desktop/merge_requests.csv"

# Fields that will appear in the output CSV file
FIELDNAMES = [
    "iid",
    "title",
    "state",
    "created_at",
    "closed_at",
    "web_url",
    "type",
    "body",
    "noteable_id",
    "author",
    "description",
]
headers = {"Private-Token": PERSONAL_ACCESS_TOKEN}


def get_all_objects_from_gitlab_api(api_endpoint, per_page=100):
    """ The GitLab API is paginated; this iterates through the pages to get
    all objects of whatever type (Merge Requests and Notes). """
    all_objects = []
    page = 1
    while True:
        url_params = {"page": page, "per_page": per_page}
        response = requests.get(api_endpoint, params=url_params, headers=headers)
        if response.status_code == 200:
            all_objects.extend(response.json())
            next_page = response.headers.get("x-next-page")
            if next_page:
                page = next_page
            else:
                break
        else:
            raise Exception(f"GitLab API request failed with status code {response.status_code}")
    return all_objects


merge_requests_api_url = f"{GITLAB_URL}/api/v4/projects/{REPO_ID}/merge_requests"
merge_requests = get_all_objects_from_gitlab_api(merge_requests_api_url)

# Open CSV file
with open(LOCAL_OUTPUT_FILE, mode="w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    writer.writerow(["object"] + FIELDNAMES)
    for merge_request in merge_requests:
        # Write a row with details on the Merge Request
        writer.writerow(
            ["merge_request"]
            + [merge_request[key] if key in merge_request else "" for key in FIELDNAMES]
        )
        notes_api_url = (
            f"{GITLAB_URL}/api/v4/projects/{REPO_ID}/merge_requests/{merge_request['iid']}/notes"
        )
        # Get all comments ("notes") for the Merge Request
        notes = get_all_objects_from_gitlab_api(notes_api_url)
        for note in notes:
            # Write a row for each note
            writer.writerow(["note"] + [note[key] if key in note else "" for key in FIELDNAMES])
