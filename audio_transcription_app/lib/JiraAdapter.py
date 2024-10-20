import requests
import json
import lib.GeminiAdapter as  GeminiAdapter 
import lib.codegen as generate_non_contextual_code, rag_code_generation
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import random


load_dotenv()


def create_jira_issue(jira_url, email, api_token, project_key, summary, description, issue_type, assignee_id):
    # Define the issue details using Atlassian Document Format for the description\
    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": description}
                        ]
                    }
                ]
            },
            "issuetype": {"name": issue_type},
            "assignee": {"id": assignee_id}
        }
    }

    # Set up headers for authentication
    headers = {"Content-Type": "application/json"}
    auth = HTTPBasicAuth(email, api_token)

    # Make a POST request to create the issue
    response = requests.post(jira_url, headers=headers, auth=auth, data=json.dumps(issue_data))

    # Check if the request was successful
    if response.status_code == 201:
        issue = response.json()
        print(f"Issue created: {issue['key']}")
    else:
        print(f"Failed to create issue: {response.text}")

# Replace with your Jira instance URL, email, and API token
jira_url = "<YOUR_JIRA_URL>"
email = "<YOUR_EMAIL>"  # Your email
api_token = os.getenv("JIRA_KEY")
# Call the function with appropriate parameters
conversation_text = """
During our meeting, we discussed several key topics. Alice mentioned that the authentication module needs to be updated to fix login issues. Bob agreed and said he would refactor the database connection code to improve performance. Charlie volunteered to start drafting the introduction section for the documentation tomorrow. Additionally, we need to implement a new feature for user profile management.
"""

summary, output = GeminiAdapter.get_email_summary_and_jira_action_items(conversation_text)

def extract_issues_and_create_tasks(output):
    for entry in output:
        # print(f"Type: {entry['type']}")
        # print(f"Issue: {entry['issue']}")
        # print(f"Description: {entry['description']}")
        # print(f"Priority: {entry['priority']}")
        # print(f"Assignee: {entry['assignee']}")
        print()  # Add a newline for better readability
        Users=["712020:a3b00c81-6c7d-4b38-b572-d6b3289ddb47","712020:da197ee0-09a2-4c56-958d-ccafd6cccb22","5fa5624cb38e610071535ee7"]
        repo_url = "https://github.com/SushaanthSrinivasan/Terminal-Todo-List-Manager" #replace with your repository URL
        # collection = fetch_and_store_code_chunks(repo_url)

        collection_name = "repodb"
        client = chromadb.PersistentClient(path="./chromadb")
        collection = client.get_collection(name=collection_name)

        query = "implement task export feature"
        non_contextual_code = generate_non_contextual_code(query, repo_url)

        generated_code = rag_code_generation(collection, non_contextual_code)
        print(generated_code)
        a_id = random.choice(Users)
        create_jira_issue(
            jira_url=jira_url,
            email=email,
            api_token=api_token,
            project_key="SCRUM",
            summary=entry['issue'],
            description=generated_code,#entry['description'],
            issue_type="Task",
            assignee_id=a_id
        )

extract_issues_and_create_tasks(output)