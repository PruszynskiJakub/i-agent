import asyncio
import json
from typing import Dict, Any

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_event, create_generation, create_span, end_generation, end_span
from models.action import ActionResult
from ynab import ynab_accounts, ynab_categories


async def execute_ynab(action, params: Dict[str, Any], trace) -> ActionResult:
   result = await take_action(action, params, trace)
   return result
       
async def take_action(action, params: Dict[str, Any], trace) -> ActionResult:
    match action:
        case "add_transaction":
            return await add_transaction(params, trace)
        case _:
            return ActionResult(
                result='Action not recognized',
                status='failed',
                documents=[]
            )

async def add_transaction(params: Dict[str, Any], trace) -> ActionResult:
    user_query = params.get("user_query")

    async def pick_amount() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_amount", "gpt-4", user_query)
        prompt = get_prompt(name="ynab_amount")
        system_prompt = prompt.compile()

        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_sides() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_sides", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_accounts")
        system_prompt = prompt.compile(
            accounts=ynab_accounts
        )
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)
    
    async def pick_category() -> Dict[str, Any]:
        generation = create_generation(trace, "pick_category", "gpt-4o", user_query)
        prompt = get_prompt(name="ynab_categories")
        system_prompt = prompt.compile(
            categories=ynab_categories
        )
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model=prompt.config.get("models", "gpt-4o"),
            json_mode=True
        )
        end_generation(generation, completion)
        return json.loads(completion)

    amount_task = asyncio.create_task(pick_amount())
    sides_task = asyncio.create_task(pick_sides())
    
    # Wait for both tasks to complete
    sides_result, amount_result = await asyncio.gather(sides_task, amount_task)
    
    category_result = None
    if 'payee' in sides_result and sides_result['payee']['type'] != 'checking':
        category_result = await pick_category()

    return ActionResult(
        result='Success',
        status='success',
        documents=[]
    )