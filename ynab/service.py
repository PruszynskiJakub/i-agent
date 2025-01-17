from typing import Dict, Any

from tools.types import ActionResult
from ynab.internal.add_transaction import add_transaction


async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            result = await add_transaction(params, trace)
            return ActionResult(
                result=result,
                documents=[]
            )
        case _:
            return ActionResult(
                result='Action not recognized',
                documents=[]
            )
