import os
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

import requests

from document.types import Document, DocumentType, DocumentMetadata
from llm.tracing import create_event


async def add_transaction(params: Dict[str, Any], trace) -> Document:
    def call_api(transactions: list) -> dict:
        if not transactions:
            raise ValueError("Missing required transactions parameter")

        url = f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions"
        headers = {
            "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url=url, json={"transactions": transactions}, headers=headers)
        
        create_event(
            trace,
            name="ynab_api_call",
            input={
                "url": url,
                "method": "POST",
                "body": {"transactions": transactions}
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

        return response.json()

    try:
        api_response = call_api(params.get("transactions", []))
        
        # Format success response
        transactions = api_response.get('data', {}).get('transactions', [])
        transaction_results = [{
            "status": "success",
            "details": {
                "details": {
                    "transaction_id": t.get('id', 'unknown'),
                    "account": t.get('account_name', 'Unknown account'),
                    "payee": t.get('payee_name', 'Unknown payee'),
                    "category": t.get('category_name', 'Not categorized'),
                }
            }
        } for t in transactions]

    except Exception as e:
        transaction_results = [{
            "status": "error",
            "error": str(e)
        }]

    doc = Document(
        uuid=uuid4(),
        conversation_uuid=params.get("conversation_uuid", ""),
        text=format_transaction_results(transaction_results),
        metadata=DocumentMetadata(
            type=DocumentType.DOCUMENT,
            source="ynab",
            description=format_document_description(transaction_results),
            name="transaction_results",
            content_type="full",
        )
    )
    return doc

def format_transaction_results(transaction_results: list) -> str:
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

def format_document_description(transaction_results: list) -> str:
    """Format a concise description of the transaction processing results."""
    total = len(transaction_results)
    successful = sum(1 for t in transaction_results if t["status"] == "success")
    failed = total - successful
    
    return f"Processed {total} transaction{'s' if total != 1 else ''}: {successful} successful, {failed} failed"
