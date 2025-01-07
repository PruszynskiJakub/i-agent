from typing import Dict, Any

from models.action import ActionResult
from ynab.internal.add_transaction import add_transaction

async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            return await add_transaction(params, trace)
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )