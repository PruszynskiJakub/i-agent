from typing import Dict, Any

from models.action import ActionResult


async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
   return ActionResult(
       result='Success',
       status='success',
       documents=[]
   )