import os
from typing import Dict, Any
import requests

from models.document import Document, DocumentType
from utils.document import create_document
from llm.tracing import create_event

async def update_transaction(params: Dict[str, Any], span) -> Document:
    """Update an existing YNAB transaction"""
    
    # Extract required transaction id
    transaction_id = params.get("id")
    if not transaction_id:
        raise ValueError("Transaction ID is required")

    # Build transaction payload with only provided fields
    # Note: amount should be in milliunits (1000 = $1.00, 12340 = $12.34)
    transaction = {"id": transaction_id}
    optional_fields = [
        "account_id", "date", "amount", "payee_id",
        "category_id", "memo", "cleared", "approved"
    ]
    
    for field in optional_fields:
        if params.get(field) is not None:
            transaction[field] = params[field]

    # Prepare request
    url = f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions"
    headers = {
        "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {"transactions": [transaction]}

    response = requests.patch(url=url, json=payload, headers=headers)
    
    create_event(
        span,
        name="ynab_api_call",
        input={
            "url": url,
            "method": "PATCH",
            "body": payload
        },
        output={
            "status_code": response.status_code,
            "body": response.json() if response.text else None
        },
        level="ERROR" if response.status_code != 200 else "DEFAULT"
    )

    if response.status_code != 200:
        error = response.json().get("error", {})
        raise Exception(f"YNAB API error: {error.get('detail', 'Unknown error')}")

    # Create success document
    updated_transaction = response.json()["data"]["transactions"][0]
    content = f"Successfully updated transaction:\n" \
             f"- ID: {updated_transaction['id']}\n" \
             f"- Amount: {updated_transaction['amount']}\n" \
             f"- Date: {updated_transaction['date']}\n" \
             f"- Memo: {updated_transaction.get('memo', 'N/A')}"

    return create_document(
        content=content,
        metadata_override={
            "type": DocumentType.DOCUMENT,
            "source": "ynab",
            "description": "Transaction update result",
            "transaction_id": updated_transaction["id"],
            "status": "success"
        }
    )
