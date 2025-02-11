import os
from typing import Dict

import aiohttp
import asyncio
import requests
import json

from dotenv import load_dotenv

# url = "https://google.serper.dev/search"
#
# payload = json.dumps({
#   "q": "site:anthropic.com",
#   "gl": "pl",
#   "tbs": "qdr:w"
# })
# headers = {
#   'X-API-KEY': os.getenv('SERPER_API_KEY'),
#   'Content-Type': 'application/json'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# print(response.text)

load_dotenv()

async def search(q) -> Dict:
    print(q)
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"site:{q['url']} {q['query']}",
        "num": 5
    }
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()

print(asyncio.run(search({"url": "anthropic.com", "query": "site:anthropic.com"})))