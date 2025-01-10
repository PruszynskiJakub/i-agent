import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

import requests

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from ynab import _ynab_accounts, _ynab_categories


async def add_transaction(params: Dict[str, Any], trace) -> str:
    query = params.get("query")

    async def split_transaction(q: str) -> list[Dict[str, Any]]:
        generation = create_generation(trace, "split_transaction", "gpt-4o", q)
        prompt = get_prompt(name="ynab_split")
        system_prompt = prompt.compile()

        try:
            completion = await open_ai.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q}
                ],
                model=prompt.config.get("model", "gpt-4o"),
                json_mode=True
            )
            end_generation(generation, completion)
            json_completion = json.loads(completion)
            return json_completion['result']
        except Exception as e:
            return [{
                "query": q,
                "error_code": "SPLIT_FAILED",
                "error_message": f"Failed to split transaction: {str(e)}"
            }]

    async def process_transaction(transaction_query: str):
        async def pick_amount(q: str) -> Dict[str, Any]:
            generation = create_generation(trace, "pick_amount", "gpt-4o", q)
            prompt = get_prompt(name="ynab_amount")
            system_prompt = prompt.compile()

            completion = await open_ai.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q}
                ],
                model=prompt.config.get("model", "gpt-4o"),
                json_mode=True
            )
            end_generation(generation, completion)
            return json.loads(completion)

        async def pick_sides(q: str) -> Dict[str, Any]:
            generation = create_generation(trace, "pick_sides", "gpt-4o", q)
            prompt = get_prompt(name="ynab_accounts")
            system_prompt = prompt.compile(
                accounts=_ynab_accounts
            )
            completion = await open_ai.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q}
                ],
                model=prompt.config.get("model", "gpt-4o"),
                json_mode=True
            )
            end_generation(generation, completion)
            return json.loads(completion)

        async def pick_category(q: str) -> Dict[str, Any]:
            generation = create_generation(trace, "pick_category", "gpt-4o", q)
            prompt = get_prompt(name="ynab_category")
            system_prompt = prompt.compile(
                categories=_ynab_categories
            )
            completion = await open_ai.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q}
                ],
                model=prompt.config.get("model", "gpt-4o"),
                json_mode=True
            )
            end_generation(generation, completion)
            return json.loads(completion)

        def call_api(sides_result: Dict[str, Any], amount_result: Dict[str, Any],
                     category_result: Dict[str, Any] | None,
                     query: str) -> Dict[str, Any]:
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
                    "memo": f"iAgent: {query}",
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

            return {
                "result": f"Added transaction '{query}'successfully"
            }

        amount_task = asyncio.create_task(pick_amount(transaction_query))
        sides_task = asyncio.create_task(pick_sides(transaction_query))

        sides_result, amount_result = await asyncio.gather(sides_task, amount_task)

        category_result = None
        if sides_result['account']['type'] == 'checking' and not (
                'payee' in sides_result and sides_result['payee']['type'] != 'checking'):
            category_result = await pick_category(transaction_query)

        transaction_details = {
            "amount_details": amount_result,
            "account_details": sides_result,
            "category_details": category_result,
        }
        api_result = call_api(sides_result, amount_result, category_result, transaction_query)
        return {**transaction_details, "api_result": api_result}

    split_results = await split_transaction(query)

    # Initialize results list with any split errors
    transaction_results = []
    valid_transactions = []
    
    for result in split_results:
        if "error_code" in result:
            transaction_results.append({
                "status": "error",
                "query": result.get("query", query),
                "error": f"Split failed: {result['error_message']}"
            })
        else:
            valid_transactions.append(result["query"])

    # If no valid transactions and no split errors, use original query
    if not valid_transactions and not transaction_results:
        valid_transactions = [query]

    # Process all valid transactions in parallel
    transaction_tasks = [process_transaction(transaction) for transaction in valid_transactions]

    # Gather results while maintaining parallel execution
    completed_results = await asyncio.gather(*transaction_tasks, return_exceptions=True)

    for transaction, result in zip(valid_transactions, completed_results):
        if isinstance(result, Exception):
            transaction_results.append({
                "status": "error",
                "query": transaction,
                "error": str(result)
            })
        else:
            transaction_results.append({
                "status": "success",
                "details": result
            })

    # Prepare summary
    total_transactions = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total_transactions - successful

    # Create a human-readable summary header
    summary = f"Processed {total_transactions} transaction{'s' if total_transactions != 1 else ''}: "
    summary += f"{successful} successful, {failed} failed\n"
    
    # Add details for all transactions
    for t in transaction_results:
        if t['status'] == 'success':
            summary += f"\n✓ {t['details']['api_result']['result']}"
        else:
            summary += f"\n✗ {t['query']}: {t['error']}"

    return summary
