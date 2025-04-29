"""
This script downloads Pull Requests and comments from an Azure DevOps
repository and writes them to a local CSV file.

First, run:
pip install azure-devops==7.1.0b4

Then fill in the CONFIGURATION AND SETUP section below. This section will need
to be unique for each repository you want to import.
"""

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.git.models import GitPullRequestSearchCriteria
import csv

# CONFIGURATION AND SETUP:
# Customize this to wherever your Azure DevOps repos are hosted, e.g.
# "https://dev.azure.com/{ORG_ID}" or "https://{ORG_ID}.visualstudio.com"
ORGANIZATION_URL = "https://{ORG_ID}.visualstudio.com/"
# In Azure DevOps, go to "User Settings" > "Personal Access Tokens" to generate
PERSONAL_ACCESS_TOKEN = "..."
# Fill in the project name and repository name on Azure DevOps
PROJECT_NAME = "..."
REPOSITORY_NAME = "..."
# Fill in the local directory you want the output CSV file to be written to
LOCAL_OUTPUT_DIRECTORY = "/home/{MY_USER_ID}/Desktop/"
# The full path of the local file you want the output written to
LOCAL_OUTPUT_FILE = f"{LOCAL_OUTPUT_DIRECTORY}azure_devops_{REPOSITORY_NAME}_pull_requests.csv"

# Connect to Azure DevOps
credentials = BasicAuthentication('', PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANIZATION_URL, creds=credentials)
git_client = connection.clients.get_git_client()

# Note: This script is intended for one repository. If you would like to fetch data from multiple repositories, you can easily modify using the following code below:
# all_projects = git_client.get_projects()
# for project in all_projects:
#     print("Project:", project.name)
#     repositories = git_client.get_repositories(project=project.name)
#     for repository in repositories:
#         print("\tRepository:", repository.name)

# How to get a specific repository attached to a specific project
repository = git_client.get_repository(
    project=PROJECT_NAME, repository_id=REPOSITORY_NAME
)
print(f"Exporting data from repository {repository.name}")

# A GitPullRequestSearchCriteria object is an optional parameter `get_pull_requests` that allows you to specify a search criteria against pull requests. This allows us to fetch merged pull requests.
search_criteria = GitPullRequestSearchCriteria(
    status=4, # PullRequestStatus.All==4 ; Setting this fetches pull requests with any status: https://learn.microsoft.com/en-us/javascript/api/azure-devops-extension-api/pullrequeststatus
    # Filter pull requests by status (non set, active, completed, abandoned, all)
    # creator_id="UserID",  # Filter pull requests created by a specific user (optional)
    # reviewer_id="UserID"  # Filter pull requests with a specific reviewer (optional)
)

all_pull_requests = []
offset = 0  # initialize offset to be zero
MAX_PAGE_SIZE = 100  # Maximum number of pull requests allowed for retrieval per page

# Retrieve pull requests in chunks ("pages") until all pull requests have been fetched
while True:
    pull_requests = git_client.get_pull_requests(
        project=PROJECT_NAME,
        repository_id=repository.id,
        search_criteria=search_criteria,
        top=MAX_PAGE_SIZE,
        skip=offset
    )
    # Add the page of pull requests to the list
    all_pull_requests.extend(pull_requests)

    # Check if we are on the last page
    if len(pull_requests) < MAX_PAGE_SIZE:
        break  # Exit the loop if all pull requests have been fetched
    else:
        offset += MAX_PAGE_SIZE  # Increment the offset parameter for the next page


# Fields that will appear in the output CSV file
PULL_REQUEST_FIELDNAMES = [
    "pull_request_id",
    "title",
    "source_ref_name",
    "closed_date",
    "creation_date",
    "description",
    "url",
    "author",
    "is_draft",
    "status",
]
COMMENT_FIELDNAMES = [
    "pull_request_id",
    "content",
    "published_date",
    "last_updated_date",
    "url",
    "author",
    "author_url",
]

# Open CSV file
with open(LOCAL_OUTPUT_FILE, mode="w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Write header row
    writer.writerow(["object"] + PULL_REQUEST_FIELDNAMES)

    for pull_request in all_pull_requests:
        # Pull Request obj fields ['additional_properties', '_links', 'artifact_id', 'auto_complete_set_by', 'closed_by', 'closed_date', 'code_review_id', 'commits', 'completion_options', 'completion_queue_time', 'created_by', 'creation_date', 'description', 'fork_source', 'is_draft', 'labels', 'last_merge_commit', 'last_merge_source_commit', 'last_merge_target_commit', 'merge_failure_message', 'merge_failure_type', 'merge_id', 'merge_options', 'merge_status', 'pull_request_id', 'remote_url', 'repository', 'reviewers', 'source_ref_name', 'status', 'supports_iterations', 'target_ref_name', 'title', 'url', 'work_item_refs']
        # Thread obj fields ['additional_properties', '_links', 'comments', 'id', 'identities', 'is_deleted', 'last_updated_date', 'properties', 'published_date', 'status', 'thread_context', 'pull_request_thread_context']
        # Comment obj fields ['additional_properties', '_links', 'author', 'comment_type', 'content', 'id', 'is_deleted', 'last_content_updated_date', 'last_updated_date', 'parent_comment_id', 'published_date', 'users_liked']
        writer.writerow(
            ["pull_request"] +
            [
                pull_request.pull_request_id,
                pull_request.title,
                pull_request.source_ref_name,
                pull_request.closed_date,
                pull_request.creation_date,
                pull_request.description,
                pull_request.url,
                pull_request.created_by.unique_name,
                pull_request.is_draft,
                pull_request.status,
            ]
        )
        threads = git_client.get_threads(
            project=PROJECT_NAME,
            repository_id=repository.id,
            pull_request_id=pull_request.pull_request_id,
        )
        if threads:
            writer.writerow(["object"] + COMMENT_FIELDNAMES)
        for thread in threads:
            for comment in thread.comments:
                # Only include comments made by users, ignore system-made comments
                if comment.comment_type == "text":
                    writer.writerow(
                        ["comment"] +
                        [
                            pull_request.pull_request_id,
                            comment.content,
                            comment.published_date,
                            comment.last_updated_date,
                            comment._links.additional_properties["self"]["href"],
                            comment.author.unique_name,
                            comment.author.url,
                        ]
                    )
    num_pull_requests = len(all_pull_requests)
    print(f"{num_pull_requests} pull requests exported into CSV file.")
