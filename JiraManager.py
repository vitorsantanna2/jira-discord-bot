from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import requests
import json

class Client:
    """
    Integration with JIRA WebService.

    https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#about
    """

    user = None
    api_token = None
    project_url = None

    def __init__(self, JIRA_PROJECT_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN):
        self.user = JIRA_USER_EMAIL
        self.api_token = JIRA_API_TOKEN
        self.project_url = JIRA_PROJECT_URL

    def _request(self, method, suffix, **kwargs):
        response = requests.request(
            method,
            urljoin(f"{self.project_url}/rest/api/3/", suffix),
            auth=HTTPBasicAuth(self.user, self.api_token),
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            **kwargs
        )
        self._handle_api_error(response)
        return response

    def _handle_api_error(self, response):
        is_json = True
        try:
            response.json()
        except ValueError:
            is_json = False

        if not is_json or not response.ok:
            raise Exception(response)

    def get_projects(self, params=None):
        """Listar todos os projetos com paginação."""
        response = self._request(
            "GET",
            f"project/search",
            params=params,
        )
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return response

    def get_tasks(self, project):
        """Listar todas as tasks de um projeto."""
        response = self._request(
            "GET",
            f"project/{project}",
            params={"include-tasks": "true"},
        )
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return response

    def get_task_by_key(self, issueKey):
        """Listar uma task."""
        response = self._request(
            "GET",
            f"issue/{issueKey}",
        )
        return response

    def get_tasks_by_sprint(self, project_key, sprint_id):
        """Listar todas as tasks de uma sprint"""

        query = {
            "jql": f"project = {project_key} AND sprint = {sprint_id}",
            "fields": "summary,customfield_10026",
        }

        response = self._request(
            "GET",
            f"search",
            params=query,
        )
        return response
