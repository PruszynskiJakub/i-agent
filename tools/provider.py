from ynab.service import execute_ynab


def get_tools():
    return [
        {
            "uuid": "a3bb189e-8bf9-4c8b-9beb-5de10a41cf62",
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc",
            "instructions": """Use the following actions based on the user's request type:
            1. ADD TRANSACTION
            {
                "action": "add_transaction",
                "params": {
                    "user_query": "an exact query from the user"
                }
            }
            Use: Creates a new transaction in the user's budget
            
            """
        }
    ]

tool_handlers = {
    "ynab" : execute_ynab
}