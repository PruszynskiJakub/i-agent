import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

import requests

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation, create_event
from models.document import Document, DocumentMetadata, DocumentType
from tools.ynab import _ynab_accounts, _ynab_categories
from utils import DEFAULT_MODEL


async def add_transaction(params: Dict[str, Any], trace) -> Document:
    query = params.get("query")

    split_results = await _split_transaction(query, trace)

    # Initialize results list with any split errors
    transaction_results = []
    valid_transactions = []

    for result in split_results:
        if "error_code" in result:
            transaction_results.append({
                "status": "error",
                "query": result.get("query", query),
                "error": f"{result['error_message']}"
            })
        else:
            valid_transactions.append(result["query"])

    # If no valid transactions and no split errors, use original query
    if not valid_transactions and not transaction_results:
        valid_transactions = [query]

    # Process all valid transactions in parallel
    transaction_tasks = [_process_transaction(transaction, trace) for transaction in valid_transactions]

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
            transaction_results.append(result)  # result already has the correct structure

    doc = Document(
        uuid=uuid4(),
        conversation_uuid=params.get("conversation_uuid", ""),
        text=_format_transaction_results(transaction_results),
        metadata=DocumentMetadata(
            type=DocumentType.DOCUMENT,
            source="ynab",
            description=_format_document_description(transaction_results),
            name="transaction_results",
            content_type="full",
        )
    )
    return doc


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

async def _process_transaction(transaction_query: str, trace):
    amount_task = asyncio.create_task(_pick_amount(transaction_query, trace))
    sides_task = asyncio.create_task(_pick_sides(transaction_query, trace))

    sides_result, amount_result = await asyncio.gather(sides_task, amount_task)

    category_result = None
    if sides_result['account']['type'] in ['checking', 'creditCard'] and (
            'payee' not in sides_result or sides_result['payee']['type'] != 'checking'):
        category_result = await _pick_category(transaction_query, trace)

    return _call_api(sides_result, amount_result, category_result, transaction_query, trace)


async def _pick_amount(q: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_amount")
    system_prompt = prompt.compile()
    generation = create_generation(trace, "pick_amount", "gpt-4o", system_prompt)

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


async def _pick_sides(q: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_accounts")
    system_prompt = prompt.compile(
        accounts=_ynab_accounts
    )
    generation = create_generation(trace, "pick_sides", "gpt-4o", system_prompt)
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


async def _pick_category(q: str, trace) -> Dict[str, Any]:
    prompt = get_prompt(name="ynab_category")
    system_prompt = prompt.compile(
        categories=_ynab_categories
    )
    generation = create_generation(trace, "pick_category", "gpt-4o", system_prompt)
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


def _call_api(sides_result: Dict[str, Any], amount_result: Dict[str, Any],
              category_result: Dict[str, Any] | None,
              query: str, trace) -> dict:
    if not sides_result or not amount_result:
        raise ValueError("Missing required parameters: sides_result and amount_result are required")

    # Get account_id safely with get() method
    account_id = sides_result.get('account', {}).get('id')
    if not account_id:
        raise ValueError("Missing required account_id in sides_result")

    # Build transaction model with safe access to nested dictionaries
    transaction = {
        "account_id": account_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": int(amount_result.get('amount', 0) * 1000),  # Convert to milliunits
        "payee_id": sides_result.get('payee', {}).get('id'),
        "payee_name": sides_result.get('payee', {}).get('name'),
        "memo": f"iAgent: {query}",
    }

    if category_result:
        transaction["category_id"] = category_result.get('category', {}).get('id')

    model = {
        "transaction": transaction
    }

    url = f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions"
    headers = {
        "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }

    response = requests.post(url=url, json=model, headers=headers)

    create_event(
        trace,
        name="ynab_api_call",
        input={
            "url": url,
            "method": "POST",
            "body": model
        },
        output={
            "status_code": response.status_code,
            "body": response.json() if response.text else None
        },
        level="ERROR" if response.status_code != 201 else "DEFAULT"
    )

    response.raise_for_status()
    if response.status_code != 201:
        raise Exception(f"Failed to add transaction: {response.text}")

    response_data = response.json()
    transaction_id = response_data.get('data', {}).get('transaction', {}).get('id', 'unknown')

    category_name = category_result.get('category', {}).get('name') if category_result else None
    account_name = sides_result.get('account', {}).get('name', 'Unknown Account')
    payee_name = sides_result.get('payee', {}).get('name', 'Unknown Payee')

    return {
        "status": "success",
        "details": {
            "details": {  # Nested details to match expected structure
                "transaction_id": transaction_id,
                "query": query,
                "category": category_name,
                "account": account_name,
                "payee": payee_name
            }
        }
    }

def _format_transaction_results(transaction_results: list) -> str:
    total_transactions = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total_transactions - successful

    # Section 1: General summary
    summary = [
        "Transaction Processing Summary",
        "----------------------------",
        f"Total transactions processed: {total_transactions}",
        f"Successful transactions: {successful}",
        f"Failed transactions: {failed}",
        ""
    ]

    # Section 2: Successful transactions
    summary.extend([
        "Successful Transactions",
        "---------------------"
    ])

    successful_transactions = [t for t in transaction_results if t["status"] == "success"]
    if successful_transactions:
        for t in successful_transactions:
            details = t.get("details", {}).get("details", {})  # Handle nested details structure
            summary.extend([
                f"Transaction ID: {details.get('transaction_id', 'Unknown')}",
                f"Description: {details.get('query', 'No description')}",
                f"Category: {details.get('category', 'Not categorized')}",
                f"Account: {details.get('account', 'Unknown account')}",
                f"Payee: {details.get('payee', 'Unknown payee')}",
                ""
            ])
    else:
        summary.append("No successful transactions\n")

    # Section 3: Failed transactions
    summary.extend([
        "Failed Transactions",
        "-----------------"
    ])

    failed_transactions = [t for t in transaction_results if t["status"] == "error"]
    if failed_transactions:
        for t in failed_transactions:
            summary.extend([
                f"Description: {t['query']}",
                f"Error: {t['error']}",
                ""
            ])
    else:
        summary.append("No failed transactions\n")

    return "\n".join(summary)


def _format_document_description(transaction_results: list) -> str:
    """Format a concise description of the transaction processing results."""
    total = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total - successful

    return f"Processed {total} transaction{'s' if total != 1 else ''}: {successful} successful, {failed} failed"