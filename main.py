import os

import requests
from todoist_api_python.api import TodoistAPI

token = os.getenv("TODOIST_API_TOKEN")
print(token)
todoist_client = TodoistAPI(token)
print(todoist_client.get_tasks(filter="search: invoice | search: faktura | search: faktury | search: faktur"))