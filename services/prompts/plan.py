from services.utils import format_tools_for_prompt


def plan_prompt(params: dict) -> str:
    formatted_tools = format_tools_for_prompt(params['tools'])

    return f"""Given the task description, current context, and key findings, determine the SINGLE NEXT STEP to take.
        
        Available tools:
        {formatted_tools}
       
        <rules>
        1. Plan only ONE next step that brings us closer to completing the task
        2. Keep any placeholders in the format [[PLACEHOLDER_NAME]]
        3. Consider the context history to avoid redundant operations
        4. Use ONLY the tools and parameters listed in the 'Available tools' section
        5. Base your decision on factual information from the key findings and context
        6. Do not introduce any information or assumptions not present in the provided data
        </rules>
        
        Respond in the following JSON format:
        {{
            "_thinking": "Explain why this specific step is the best next action, referencing key findings or context",
             "step": "description of the single next step",
            "tool_name": "exact name of the tool to use from the available tools",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}"""