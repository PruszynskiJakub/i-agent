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

    def call_api(sides_result: Dict[str, Any], amount_result: Dict[str, Any], category_result: Dict[str, Any] | None, user_query: str):
        if not sides_result or not amount_result:
            raise ValueError("Missing required parameters: sides_result and amount_result are required")

        # Get account_id safely with get() method
        account_id = sides_result.get('account', {}).get('id')
        if not account_id:
            raise ValueError("Missing required account_id in sides_result")

        # Build transaction model with safe access to nested dictionaries
        model = {
            "transaction": {
                "account_id": account_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "amount": int(amount_result.get('amount', 0) * 1000),  # Convert to milliunits
                "payee_id": sides_result.get('payee', {}).get('id'),
                "payee_name": sides_result.get('payee', {}).get('name'),
                "category_id": category_result.get('category', {}).get('id') if category_result else None,
                "memo": f"iAgent: {user_query}",
            }
        }

        response = requests.post(
            url=f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions",
            json=model,
            headers={
                "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        if response.status_code != 201:
            raise Exception(f"Failed to add transaction: {response.text}")

    async def process_transaction(transaction_query: str):
        amount_task = asyncio.create_task(pick_amount(transaction_query))
        sides_task = asyncio.create_task(pick_sides(transaction_query))
        
        sides_result, amount_result = await asyncio.gather(sides_task, amount_task)
        
        category_result = None
        if sides_result['account']['type'] == 'checking' and not('payee' in sides_result and sides_result['payee']['type'] != 'checking'):
            category_result = await pick_category()

        call_api(sides_result, amount_result, category_result, transaction_query)

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

    # Process all transactions in parallel
    await asyncio.gather(*[
        process_transaction(transaction["query"]) 
        for transaction in valid_transactions
    ])

    return ActionResult(
        result='Success',
        status='success',
        documents=[]
    )