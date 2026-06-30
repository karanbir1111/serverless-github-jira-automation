import json
import os
import requests
from requests.auth import HTTPBasicAuth

def lambda_handler(event, context):
    try:
        # 1. Safely extract and parse the GitHub webhook JSON data payload
        raw_body = event.get("body", "{}")
        payload = json.loads(raw_body)
        
        # 2. Extract the comment text to check for the keyword trigger
        comment_body = payload.get("comment", {}).get("body", "")
        
        # 3. Conditional Check: Only run automation if the comment is exactly '/jira'
        if comment_body.strip() != "/jira":
            print(f"Skipping: Comment '{comment_body}' does not match trigger keyword '/jira'")
            return {
                "statusCode": 200,
                "body": json.dumps("Skipping: Trigger keyword not matched.")
            }
            
        # 4. Extract all rich issue details from the GitHub payload
        github_issue = payload.get("issue", {})
        issue_title = github_issue.get("title", "No Title Provided")
        issue_body = github_issue.get("body", "No description provided by the author.")
        issue_url = github_issue.get("html_url", "")
        issue_number = github_issue.get("number", "N/A")
        issue_user = github_issue.get("user", {}).get("login", "Unknown User")
        
        # 5. Ingest infrastructure secrets from the cloud environment variables
        jira_email = os.environ.get("JIRA_EMAIL")
        jira_token = os.environ.get("JIRA_API_TOKEN")
        jira_url = os.environ.get("JIRA_URL")  # Format: https://your-domain.atlassian.net/rest/api/3/issue
        jira_project_key = os.environ.get("JIRA_PROJECT_KEY")

        if not all([jira_email, jira_token, jira_url, jira_project_key]):
            raise ValueError("Configuration Error: Missing one or more active environment variables.")

        # 6. Formulate authentication and request headers for Jira REST API v3
        auth = HTTPBasicAuth(jira_email, jira_token)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Construct rich summary and descriptive text strings combining all details
        jira_summary = f"[GH-{issue_number}] {issue_title}"
        formatted_description_text = (
            f"Opened by: {issue_user}\n"
            f"Original Issue Link: {issue_url}\n\n"
            f"--- GitHub Issue Description ---\n"
            f"{issue_body}"
        )
        
        # 7. Map GitHub metadata to Jira Document Format structure
        jira_payload = {
            "fields": {
                "project": {
                    "key": jira_project_key
                },
                "summary": jira_summary,
                "description": {
                    "version": 1,
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": formatted_description_text
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": "Task"
                }
            }
        }
        
        # 8. Dispatch the POST request with an integrated 10-second request timeout
        response = requests.post(jira_url, json=jira_payload, headers=headers, auth=auth, timeout=10)
        
        # Automatically throw an error structure for 4xx or 5xx failures
        response.raise_for_status()
        
        print(f"Success: Jira ticket created successfully for GitHub Issue #{issue_number}.")
        return {
            "statusCode": 201,
            "body": json.dumps("Jira issue provisioned successfully with full details.")
        }

    except Exception as e:
        print(f"Automation Script Execution Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Internal Automation Failure: {str(e)}")
        }
