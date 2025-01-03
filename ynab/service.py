import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

import requests

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.action import ActionResult
from ynab import _ynab_accounts, _ynab_categories


async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
   result = await _take_action(action, params, trace)
   return result
       
async def _take_action(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            return await _add_transaction(params, trace)
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )

async def split_transaction(user_query: str, trace) -> list[Dict[str, Any]]:
    generation = create_generation(trace, "split_transaction", "gpt-4o", user_query)
    prompt = get_prompt(name="ynab_split")
    system_prompt = prompt.compile()

    try:
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    except Exception as e:
        return [{
            "query": user_query,
            "error_code": "SPLIT_FAILED",
            "error_message": f"Failed to split transaction: {str(e)}"
        }]

async def _add_transaction(params: Dict[str, Any], trace) -> ActionResult:
    user_query = params.get("user_query")
    
    async def split_transaction(user_query: str) -> list[Dict[str, Any]]:
        generation = create_generation(trace, "split_transaction", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_split")
        system_prompt = prompt.compile()

        try:
            completion = await open_ai.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                model=prompt.config.get("model", "gpt-4o"),
                json_mode=True
            )
            end_generation(generation, completion)
            return json.loads(completion)
        except Exception as e:
            return [{
                "query": user_query,
                "error_code": "SPLIT_FAILED",
                "error_message": f"Failed to split transaction: {str(e)}"
            }]

    async def pick_amount() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_amount", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_amount")
        system_prompt = prompt.compile()

        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_sides() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_sides", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_accounts")
        system_prompt = prompt.compile(
            accounts=_ynab_accounts
        )
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_category() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_category", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_category")
        system_prompt = prompt.compile(
            categories=_ynab_categories
        )   
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("model1", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)

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

    split_results = await split_transaction(user_query)
    
    # Filter out and print errors, keep valid transactions
    valid_transactions = []
    for result in split_results:
        if "error_code" in result:
            print(f"Split failed for transaction: {result['error_message']}")
        else:
            valid_transactions.append(result)

    # If no valid transactions, use original query
    if not valid_transactions:
        valid_transactions = [{"query": user_query}]

    # Process each valid transaction in parallel
    transaction_tasks = []
    for transaction in valid_transactions:
        amount_task = asyncio.create_task(pick_amount(transaction["query"]))
        sides_task = asyncio.create_task(pick_sides(transaction["query"]))
        transaction_tasks.append((amount_task, sides_task))

    # Wait for all transactions to be processed
    for amount_task, sides_task in transaction_tasks:
        sides_result, amount_result = await asyncio.gather(sides_task, amount_task)
        
        category_result = None
        if sides_result['account']['type'] == 'checking' and not('payee' in sides_result and sides_result['payee']['type'] != 'checking'):
            category_result = await pick_category()

        call_api()  # Process each transaction

    return ActionResult(
        result='Success',
        status='success',
        documents=[]
    )