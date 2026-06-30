# Serverless GitHub-to-Jira Cross-Platform Automation

An event-driven cloud automation tool written in Python and deployed on AWS Lambda. This integration seamlessly extracts metadata from rich inbound GitHub Webhook payloads to dynamically provision tracked tasks via the Atlassian Jira REST API v3.

## 🚀 Architecture Workflow
Unlike traditional approaches utilizing continuously running virtual servers (e.g., EC2) which introduce unnecessary cost and maintenance overhead, this project adopts a **Cloud-Native, Serverless** design pattern:

1. **The Event Trigger:** A developer comments exactly `/jira` on a GitHub issue thread.
2. **The Webhook Dispatch:** GitHub triggers an HTTP POST request carrying a detailed JSON payload of the issue metadata.
3. **The Compute Layer:** AWS Lambda instantiates an on-demand Python 3.12 environment instantly to capture the request.
4. **The Processing Core:** The script performs validation filtering, parses nested data blocks safely, and authenticates against the Atlassian REST endpoint.
5. **The Synchronization:** A structured, context-rich ticket is seamlessly generated in Jira for tracking.

## 🛠️ Technology Stack & Frameworks
* **Language:** Python 3.12
* **Cloud Architecture:** AWS Lambda (Serverless Compute)
* **API Frameworks:** GitHub Webhooks Engine, Atlassian Jira REST API v3
* **Core Libraries:** Requests (HTTP Client Engine), JSON parsing, OS engine

## 🛡️ Production Engineering Standards Implemented

### 1. Robust Metadata Mapping
Rather than copying only basic titles, the automation extracts the full operational footprint of an issue—capturing the **Issue Identifier**, **Title**, **Description Markdown Body**, **Reporter Profile Handle**, and an explicit **Cross-Reference URL Link** back to source control.

### 2. Strict Conditional Keyword Triggering
Engineered a text-parsing filter layer (`if comment_body.strip() != "/jira"`) ensuring that normal, everyday developer discussions on issue boards do not generate noise or duplicate records within project boards.

### 3. Separation of Concerns & Security Hardening
Adheres strictly to the principles of zero hardcoded configuration secrets. Leveraged Python's native `os.environ` module to securely inject API keys and workspace domains at runtime, maintaining absolute code isolate-cleanliness within the open source repository.

### 4. Defensive Software Design
Wrapped critical network request pathways inside standard `try-except` blocks. Features custom, granular exception logging along with explicit network timeouts (`timeout=10`) to gracefully prevent serverless function hangs and map cloud-runtime execution anomalies cleanly into monitoring dashboards.

## 📦 Repository Structure
```text
serverless-github-jira-automation/
├── src/
│   └── lambda_function.py     # Main event handler execution script
├── README.md                  # Eloquent system architecture documentation
└── requirements.txt           # Declared project runtime dependencies
## 📋 Installation & Deployment Guide

Follow these steps to deploy this serverless automation tool into your own cloud environment:

### 1. Jira Authentication Configuration
* Navigate to [Atlassian API Token Management](https://id.atlassian.com/manage-profile/security/api-tokens) and generate a new token.
* Note your target Jira **Project Key** (e.g., `DEV`) from your project board settings.

### 2. AWS Lambda Provisioning
* Create a new AWS Lambda function from scratch using the **Python 3.12** runtime environment.
* Attach a public `requests` library Layer to the function based on your AWS region (e.g., using the community Klayers project ARNs) to support external HTTP requests.
* Copy the source code from `src/lambda_function.py` into the online code editor and click **Deploy**.

### 3. Secure Environment Configurations
Navigate to **Configuration > Environment variables** within your Lambda console and securely inject the following four key-value pairs:
* `JIRA_EMAIL` — Your Atlassian account login email.
* `JIRA_API_TOKEN` — The secure API token generated in Step 1.
* `JIRA_PROJECT_KEY` — Your capitalized target project abbreviation key.
* `JIRA_URL` — Your workspace endpoint (e.g., `https://your-domain.atlassian.net/rest/api/3/issue`).

### 4. Expose the Serverless Endpoint
* In the Lambda configuration tab, navigate to **Function URL** and click **Create Function URL**.
* Set the **Auth type** to `NONE` to allow incoming webhooks from external networks, and copy the generated public HTTPS URL string.

### 5. Wire Up the GitHub Webhook
* Go to your GitHub repository and open **Settings > Webhooks > Add Webhook**.
* Paste your AWS Lambda **Function URL** into the *Payload URL* field.
* Modify the *Content type* selection dropdown to `application/json`.
* Under event triggers, choose **Let me select individual events**, uncheck *Pushes*, and check **Issue comments**. Click **Add Webhook** to activate the automation.
