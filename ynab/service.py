from typing import Dict, Any

from tools.types import ActionResult, ActionStatus
from ynab.internal.add_transaction import add_transaction

async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            result = await add_transaction(params, trace)
            # Check if the result contains any failure indicators
            status = ActionStatus.SUCCESS if "failed" not in result.lower() else ActionStatus.FAILURE
            return ActionResult(
                result=result,
                status=status,
                documents=[]
            )
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )
