import os
from typing import Dict, Any

import requests

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document


async def _update_transaction(params: Dict[str, Any], span) -> Document:
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

    response = requests.patch(
        url=f"{os.getenv('YNAB_BASE_URL')}/budgets/{os.getenv('YNAB_BUDGET_ID')}/transactions",
        json={"transactions": [transaction]},
        headers={
            "Authorization": f"Bearer {os.getenv('YNAB_PERSONAL_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }
    )

    create_event(
        span,
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
        level="ERROR" if response.status_code != 200 else "DEFAULT"
    )

    if response.status_code != 200:
        error = response.json().get("error", {})
        return create_error_document(
            error=Exception(f"Updating transaction with id {transaction_id} failed"),
            error_context=f"YNAB API error: {error.get('detail', 'Unknown error')}",
            conversation_uuid=params.get("conversation_uuid", "unknown")
        )

    # Format the results
    updated_transaction = response.json()["data"]["transactions"][0]
    result = (
        f"Update Transaction Result\n"
        f"----------------------\n"
        f"Transaction ID: {updated_transaction['id']}\n"
        f"Amount: {updated_transaction['amount']}\n"
        f"Date: {updated_transaction['date']}\n"
        f"Memo: {updated_transaction.get('memo', 'N/A')}\n"
    )

    return create_document(
        text=result,
        metadata_override={
            "type": DocumentType.DOCUMENT,
            "source": "ynab",
            "name": "UpdateTransactionsResult",
            "conversation_uuid": params.get("conversation_uuid", ""),
            "description": f"Updated transaction with id {transaction_id}",
            "content_type": "full"
        }
    )
