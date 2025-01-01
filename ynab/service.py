import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

import requests

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_event, create_generation, create_span, end_generation, end_span
from models.action import ActionResult
from ynab import ynab_accounts, ynab_categories


async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
   result = await take_action(action, params, trace)
   return result
       
async def take_action(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            return await add_transaction(params, trace)
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )

async def add_transaction(params: Dict[str, Any], trace) -> ActionResult:
    user_query = params.get("user_query")

    async def pick_amount() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_amount", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_amount")
        system_prompt = prompt.compile()

        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_sides() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_sides", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_accounts")
        system_prompt = prompt.compile(
            accounts=ynab_accounts
        )
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_category() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_category", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_category")
        system_prompt = prompt.compile(
            categories=ynab_categories
        )   
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)



    amount_task = asyncio.create_task(pick_amount())
    sides_task = asyncio.create_task(pick_sides())
    
    # Wait for both tasks to complete
    sides_result, amount_result = await asyncio.gather(sides_task, amount_task)
    
    category_result = None
    if sides_result['account']['type'] == 'checking' and not('payee' in sides_result and sides_result['payee']['type'] != 'checking'):
        category_result = await pick_category()

    def call_api():
        model = {
          "transaction": {
            "account_id": sides_result['account']['id'],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount_result['amount'] * 1000,# Convert to milliunits
            "payee_id": sides_result['payee']['id'] if 'payee' in sides_result else None,
            "payee_name": sides_result['payee']['name'] if 'payee' in sides_result else None,
            "category_id": category_result['category']['id'] if category_result else None,
            "memo": "iAgent: " + user_query,
          }
        }

        response = requests.post(
            url=f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv("YNAB_BUDGET_ID")}/transactions",
            json=model,
            headers={
                "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        if response.status_code != 201:
            raise Exception(f"Failed to add transaction: {response.text}")

    call_api()

    return ActionResult(
        result='Success',
        status='success',
        documents=[]
    )