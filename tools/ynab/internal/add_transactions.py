import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

import requests

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation, create_event
from models.document import Document, DocumentType
from tools.ynab import _ynab_accounts, _ynab_categories
from utils import DEFAULT_MODEL
from utils.document import create_document


async def _add_transactions(params: Dict[str, Any], trace) -> Document:
    query = params.get("query")

    split_results = await _split_transaction(query, trace)

    # Initialize results list with any split errors
    transaction_results = []
    transaction_queries = []

    for result in split_results:
        if "error_code" in result:
            transaction_results.append({
                "status": "error",
                "query": result.get("query", query),
                "error": result['error_message']
            })
        else:
            transaction_queries.append(result["query"])

    # If no valid transactions and no split errors, use original query
    if not transaction_queries and not transaction_results:
        transaction_queries = [query]

    # Process all valid transactions in parallel
    transaction_tasks = [_process_transaction(transaction, trace) for transaction in transaction_queries]

    # Gather results while maintaining parallel execution
    transaction_models = await asyncio.gather(*transaction_tasks, return_exceptions=True)

    # Separate successful models and errors
    valid_transactions = []
    for transaction_query, result in zip(transaction_queries, transaction_models):
        if isinstance(result, Exception):
            transaction_results.append({
                "status": "error",
                "query": transaction_query,
                "error": str(result)
            })
        else:
            valid_transactions.append(result)

    # Make single API call if we have valid transactions
    if valid_transactions:
        try:
            response = requests.post(
                url=f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions",
                json={
                    "transactions": valid_transactions
                },
                headers={
                    "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
                    "Content-Type": "application/json"
                }
            )

            create_event(
                trace,
                name="ynab_api_call",
                input={
                    "url": response.request.url,
                    "method": response.request.method,
                    "body": response.request.body
                },
                output={
                    "status_code": response.status_code,
                    "body": response.json() if response.text else None
                },
                level="ERROR" if response.status_code != 201 else "DEFAULT"
            )

            if response.status_code != 201:
                error = response.json()['error']
                raise Exception(f"Failed to add transactions. Details: {error.get('detail', 'Unknown error')}")

            response_data = response.json()
            transactions = response_data.get('data', {}).get('transactions', [])

            # Map successful transactions to results
            for transaction, model in zip(transactions, valid_transactions):
                transaction_results.append({
                    "status": "success",
                    "details": {
                        "transaction_id": transaction.get('id', 'unknown'),
                        "query": model['memo'].replace('iAgent: ', ''),
                        "category": model.get('category_name', 'Not categorized'),
                        "account": model.get('account_name', 'Unknown Account'),
                        "payee": model.get('payee_name', 'Unknown Payee')
                    }
                })

        except Exception as e:
            # If bulk API call fails, mark all valid transactions as failed
            for model in valid_transactions:
                transaction_results.append({
                    "status": "error",
                    "query": model['memo'].replace('iAgent: ', ''),
                    "error": str(e)
                })

    return create_document(
        text=_format_transaction_results(transaction_results),
        metadata_override={
            "conversation_uuid": params.get("conversation_uuid", ""),
            "source": "ynab",
            "name": "AddingTransactionsResult",
            "description": _format_document_description(transaction_results),
            "type": DocumentType.DOCUMENT,
            "content_type": "full",
        }
    )


async def _split_transaction(query: str, trace) -> list[Dict[str, Any]]:
    prompt = get_prompt(name="ynab_split")
    system_prompt = prompt.compile()
    model = prompt.config.get("model", DEFAULT_MODEL)

    generation = create_generation(
        trace,
        "split_transaction",
        model,
        system_prompt
    )

    try:
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model=model,
            json_mode=True
        )
        end_generation(generation, completion)
        json_completion = json.loads(completion)
        return json_completion['result']
    except Exception as e:
        return [{
            "query": query,
            "error_code": "SPLIT_FAILED",
            "error_message": f"Failed to split transaction: {str(e)}"
        }]


async def _pick_amount(query: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_amount")
    system_prompt = prompt.compile()
    model = prompt.config.get("model", DEFAULT_MODEL)
    generation = create_generation(trace, "pick_amount", model, system_prompt)

    completion = await open_ai.completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        model=model,
        json_mode=True
    )
    end_generation(generation, completion)
    return json.loads(completion)


async def _pick_sides(query: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_accounts")
    system_prompt = prompt.compile(
        accounts=_ynab_accounts
    )
    model = prompt.config.get("model", DEFAULT_MODEL)

    generation = create_generation(trace, "pick_sides", model, system_prompt)
    completion = await open_ai.completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        model=model,
        json_mode=True
    )
    end_generation(generation, completion)
    return json.loads(completion)


async def _pick_category(query: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_category")
    system_prompt = prompt.compile(
        categories=_ynab_categories
    )
    model = prompt.config.get("model", DEFAULT_MODEL)

    generation = create_generation(trace, "pick_category", model, system_prompt)
    completion = await open_ai.completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        model=model,
        json_mode=True
    )
    end_generation(generation, completion)
    return json.loads(completion)


async def _process_transaction(transaction_query: str, trace) -> dict:
    """Process a single transaction and return the transaction model for the API."""
    if not transaction_query:
        raise ValueError("Missing required transaction query")

    amount_task = asyncio.create_task(_pick_amount(transaction_query, trace))
    sides_task = asyncio.create_task(_pick_sides(transaction_query, trace))

    sides_result, amount_result = await asyncio.gather(sides_task, amount_task)

    if not sides_result or not amount_result:
        raise ValueError("Missing required parameters: sides_result and amount_result")

    account_id = sides_result.get('account', {}).get('id')
    if not account_id:
        raise ValueError("Missing required account_id in sides_result")

    # Build transaction model
    transaction = {
        "account_id": account_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": int(amount_result.get('amount', 0) * 1000),  # Convert to milliunits
        "payee_id": sides_result.get('payee', {}).get('id'),
        "payee_name": sides_result.get('payee', {}).get('name'),
        "memo": f"iAgent: {transaction_query}",
        "account_name": sides_result.get('account', {}).get('name'),  # Store for result formatting
    }

    # Get category if needed
    if sides_result['account']['type'] in ['checking', 'creditCard'] and (
            'payee' not in sides_result or sides_result['payee']['type'] != 'checking'):
        category_result = await _pick_category(transaction_query, trace)
        if category_result:
            transaction["category_id"] = category_result.get('category', {}).get('id')
            transaction["category_name"] = category_result.get('category', {}).get('name')

    return transaction


def _format_transaction_results(transaction_results: list) -> str:
    total = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total - successful

    result = (
            f"Transaction Summary\n"
            f"------------------\n"
            f"Total transactions processed: {total}\n"
            f"Successfully added: {successful}\n"
            f"Failed adds: {failed}\n\n"
            f"Successfully Added Transactions\n"
            f"----------------------------\n"
            + (
                "\n".join(
                    f"Transaction ID: {t['details']['transaction_id']}\n"
                    f"Description: {t['details']['query']}\n"
                    f"Category: {t['details'].get('category', 'Not categorized')}\n"
                    f"Account: {t['details']['account']}\n"
                    f"Payee: {t['details']['payee']}\n"
                    for t in transaction_results if t["status"] == "success"
                ) if any(t["status"] == "success" for t in transaction_results)
                else "No transactions were successfully added"
            )
            + "\n\nFailed Transactions\n-------------------\n"
            + (
                "\n".join(
                    f"Description: {t['query']}\n"
                    f"Error: {t['error']}\n"
                    for t in transaction_results if t["status"] == "error"
                ) if any(t["status"] == "error" for t in transaction_results)
                else "No failed transactions"
            )
    )

    return result


def _format_document_description(transaction_results: list) -> str:
    """Format a concise description of the transaction processing results."""
    total = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total - successful

    return f"Processed {total} transaction{'s' if total != 1 else ''}: {successful} successful, {failed} failed"
