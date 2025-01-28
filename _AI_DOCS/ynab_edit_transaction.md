PATCH : /budgets/{budget_id}/transactions

Reqeust body:
{
  "transactions": [
    {
      "id": "string",
      "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "date": "2025-01-28",
      "amount": 0,
      "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "memo": "string",
      "cleared": "cleared",
      "approved": true,
    }
  ]
}

Response:
- Success:
  - http code 209
  - body:
  - {
    "data": {
      "transactions": [
      {
        "id": "string",
        "date": "2025-01-28",
        "amount": 0,
        "memo": "string",
        "cleared": "cleared",
        "approved": true,
        "flag_color": "red",
        "flag_name": "string",
        "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "transfer_transaction_id": "string",
        "matched_transaction_id": "string",
        "import_id": "string",
        "import_payee_name": "string",
        "import_payee_name_original": "string",
        "debt_transaction_type": "payment",
        "deleted": true,
        "account_name": "string",
        "payee_name": "string",
        "category_name": "string",
        "subtransactions": [
          {
            "id": "string",
            "transaction_id": "string",
            "amount": 0,
            "memo": "string",
            "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "payee_name": "string",
            "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "category_name": "string",
            "transfer_account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "transfer_transaction_id": "string",
            "deleted": true
          }
        ]
      }
    ],
    "duplicate_import_ids": [
      "string"
    ],
    "server_knowledge": 0
  }
}

- error
  - http code 400
  - body:{
  "error": {
    "id": "string",
    "name": "string",
    "detail": "string"
  }
}