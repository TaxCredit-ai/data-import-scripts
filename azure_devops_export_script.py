"""
This script downloads Pull Requests and comments from an Azure DevOps
repository and writes them to a local CSV file.

First, run:
pip install azure-devops==6.0.0b4

Then fill in the CONFIGURATION AND SETUP section below. This section will need
to be unique for each repository you want to import.
"""

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.models import GitPullRequestSearchCriteria
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


# Connect to Azure DevOps
credentials = BasicAuthentication('', PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANIZATION_URL, creds=credentials)
git_client = connection.clients.get_git_client()
# How to get all projects
# all_projects = git_client.get_projects()
# for project in all_projects:
#     print("Project:", project.name)
#     # Get all repositories in the project
#     repositories = git_client.get_repositories(project=project.name)
#     for repository in repositories:
#         print("\tRepository:", repository.name)
# How to get specific repository that is attached specific project
repository = git_client.get_repository(
    project=PROJECT_NAME, repository_id=REPOSITORY_NAME
)
# Printing repository data for testing
# branches = git_client.get_branches(project=project_name, repository_id=repository.id)
# print("Branches in the repository:")
# for branch in branches:
#     print(branch.name)
# Optionally specify a search criteria against pull requests
search_criteria = GitPullRequestSearchCriteria(
    status="completed",
    # Filter pull requests by status (active, completed, abandoned)
    # creator_id="UserID",  # Filter pull requests created by a specific user (optional)
    # reviewer_id="UserID"  # Filter pull requests with a specific reviewer (optional)
)
# Fetch merged pull requests
merged_pull_requests = git_client.get_pull_requests(
    project=PROJECT_NAME,
    repository_id=repository.id,
    search_criteria=search_criteria,  # Optional GitPullRequestSearchCriteria instance
    top=None,  # Optionally specify the maximum number of pull requests to retrieve
)
# Fetch open pull requests
open_pull_requests = git_client.get_pull_requests(
    project=PROJECT_NAME,
    repository_id=repository.id,
    search_criteria=None,  # defaults to searching for pull requests with "active" status
    top=None,  # Optionally specify the maximum number of pull requests to retrieve
)
pull_requests_search = merged_pull_requests + open_pull_requests
for pull_request in pull_requests_search:
    """
    Pull Request obj fields ['additional_properties', '_links', 'artifact_id', 'auto_complete_set_by', 'closed_by', 'closed_date', 'code_review_id', 'commits', 'completion_options', 'completion_queue_time', 'created_by', 'creation_date', 'description', 'fork_source', 'is_draft', 'labels', 'last_merge_commit', 'last_merge_source_commit', 'last_merge_target_commit', 'merge_failure_message', 'merge_failure_type', 'merge_id', 'merge_options', 'merge_status', 'pull_request_id', 'remote_url', 'repository', 'reviewers', 'source_ref_name', 'status', 'supports_iterations', 'target_ref_name', 'title', 'url', 'work_item_refs']
    """
    print(
        f"\nPull Request #{pull_request.pull_request_id}: {pull_request.title} (Status: {pull_request.status})"
    )
    print(f"URL: {pull_request.url}")
    # desired fields
    print(pull_request.pull_request_id)
    print(pull_request.merge_id)
    print(pull_request.title)
    print(pull_request.description)
    print(pull_request.status)
    print(pull_request.merge_status)
    print(pull_request.url)
    print(pull_request.created_by.unique_name)
    print(pull_request.creation_date)
    print(pull_request.closed_date)
    # Get all threads in the pull request
    threads = git_client.get_threads(
        project=PROJECT_NAME,
        repository_id=repository.id,
        pull_request_id=pull_request.pull_request_id,
    )
    for thread in threads:
        """
        Thread obj fields ['additional_properties', '_links', 'comments', 'id', 'identities', 'is_deleted', 'last_updated_date', 'properties', 'published_date', 'status', 'thread_context', 'pull_request_thread_context']
        """
        print(f"\tThread {thread.id}")
        for comment in thread.comments:
            """
            Comment obj fields ['additional_properties', '_links', 'author', 'comment_type', 'content', 'id', 'is_deleted', 'last_content_updated_date', 'last_updated_date', 'parent_comment_id', 'published_date', 'users_liked']
            """
            print(f"\t\tComment: {comment.content}")
            # desired fields
            print(comment.author.unique_name)
            print(comment.id)
            print(comment.content)
            print(comment.published_date)
            print(comment.last_updated_date)
            print(
                comment._links.additional_properties["self"]["href"]
            )  # This is an API response. Haven't been able to find the comment anchor tag ID e.g. "1711659975"
# The full path of the local file you want the output written to
local_output_file = f"{LOCAL_OUTPUT_DIRECTORY}azure_devops_{REPOSITORY_NAME}_pull_requests.csv"
# Fields that will appear in the output CSV file
PULL_REQUEST_FIELDNAMES = [
    "pull_request_id",
    "merge_id",
    "title",
    "status",
    "merge_status",
    "author",
    "creation_date",
    "closed_date",
    "description",
    "url",
]
COMMENT_FIELDNAMES = ["content", "published_date", "last_updated_date", "url", "author"]
# Open CSV file
with open(local_output_file, mode="w", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Write header row
    writer.writerow(["object"] + PULL_REQUEST_FIELDNAMES)
    for pull_request in pull_requests_search:
        writer.writerow(
            ["pull_request"] +
            [
                pull_request.pull_request_id,
                pull_request.merge_id,
                pull_request.title,
                pull_request.status,
                pull_request.merge_status,
                pull_request.created_by.unique_name,
                pull_request.creation_date,
                pull_request.closed_date,
                pull_request.description,
                pull_request.url,
            ]
        )
        # [getattr(pull_request, key) if key in pull_request.__dict__ else "" for key in PULL_REQUEST_FIELDNAMES]
        if threads:
            writer.writerow(["object"] + COMMENT_FIELDNAMES)
        threads = git_client.get_threads(
            project=PROJECT_NAME,
            repository_id=repository.id,
            pull_request_id=pull_request.pull_request_id,
        )
        for thread in threads:
            for comment in thread.comments:
                writer.writerow(
                    ["comment"] +
                    [
                        comment.content,
                        comment.published_date,
                        comment.last_updated_date,
                        comment._links.additional_properties["self"]["href"],
                        comment.author.unique_name,
                    ]
                )
