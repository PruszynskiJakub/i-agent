from typing import Dict, Any

from tools.types import ActionResult
from ynab.internal.add_transaction import add_transaction

async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            result_summary = await add_transaction(params, trace)
            return ActionResult(
                result=str(result_summary),
                status=ActionStatus.SUCCESS if result_summary["summary"]["failed"] == 0 else ActionStatus.FAILURE,
                documents=[]
            )
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )
