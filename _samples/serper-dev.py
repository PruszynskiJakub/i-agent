import os

import requests
import json

url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "site:anthropic.com",
  "gl": "pl",
  "tbs": "qdr:w"
})
headers = {
  'X-API-KEY': os.getenv('SERPER_API_KEY'),
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)