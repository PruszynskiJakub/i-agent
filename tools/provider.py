from ynab.service import execute_ynab


def get_tools():
    return [
        {
            "uuid": "a3bb189e-8bf9-4c8b-9beb-5de10a41cf62",
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc",
            "instructions": "",
        }
    ]

tool_handlers = {
    "ynab" : execute_ynab
}