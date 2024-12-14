import json
from typing import List, Dict, Any
import uuid
from modules.logging_service import log_info, log_error, log_tool_call
from modules.openai_service import OpenAIService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangfuseService
from modules.web_service import WebService
from modules.document_service import DocumentService
from modules.types import State, Action
from modules.utils import format_actions_for_prompt, format_tools_for_prompt

class AgentService:
    def __init__(self, state: State, openai_service: OpenAIService, db_service: DatabaseService, 
                 langfuse_service: LangfuseService, web_service: WebService, document_service: DocumentService):
        self.state = state
        self.openai_service = openai_service
        self.db_service = db_service
        self.langfuse_service = langfuse_service
        self.web_service = web_service
        self.document_service = document_service

    async def run(self, messages: List[Dict[str, Any]], parent_trace=None) -> str:
        self.db_service.store_message(self.state.conversation_uuid, "user", messages[-1]['content'])

        while self.state.config["current_step"] < self.state.config["max_steps"]:
            # Plan phase
            plan_result = await self._plan(messages, parent_trace)
            
            # If the tool is final_answer, return empty string
            if plan_result["tool"] == "final_answer":
                break
                
            # Execute phase
            await self._execute(plan_result, parent_trace)
            
            # Increment step counter at end of loop
            self.state.config["current_step"] += 1
            
        # Get final answer using answer method
        final_answer = await self._answer(messages, parent_trace)

        self.db_service.store_message(self.state.conversation_uuid, "assistant", final_answer)
        
        return final_answer

    async def _plan(self, messages: List[Dict[str, Any]], parent_trace=None) -> Dict[str, Any]:
        try:
            # Get system prompt
            prompt = self.langfuse_service.get_prompt(
                name="agent_plan",
                prompt_type="text",
                label="latest"
            )
            
            # Compile the prompt with any needed variables
            system_prompt = prompt.compile(
                formatted_tools=format_tools_for_prompt(self.state.tools),
                taken_actions=format_actions_for_prompt(self.state.actions)
            )
            
            # Get model from prompt config, fallback to default if not specified
            model = prompt.config.get("model", "gpt-4o-mini")
            
            # Create generation observation under the main trace
            generation = parent_trace.generation(
                name="agent_plan",
                model=model,  # Use model from prompt config
                input=system_prompt,
                metadata={
                    "conversation_id": self.state.conversation_uuid
                }
            )
            
            # Get AI response with JSON mode enabled
            completion = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model,
                json_mode=True
            )
            
            # Parse the response as JSON
            try:
                response_data = json.loads(completion)
                log_info(f"Plan generated: {response_data}", style="bold blue")
            except json.JSONDecodeError as e:
                log_error(f"Failed to parse JSON response: {str(e)}")
                response_data = {}
            
            # Update generation with the response
            generation.end(
                output=response_data,
            )

            return response_data
            
        except Exception as e:
            raise Exception(f"Error in agent service: {str(e)}")

    async def _execute(self, plan: Dict[str, Any], parent_trace=None):
        log_info(f"Executing plan with tool: {plan.get('tool', 'unknown')}", style="bold cyan")
        
        # Validate plan structure
        required_fields = ["_thinking", "step", "tool", "parameters", "required_information"]
        if not all(field in plan for field in required_fields):
            error_msg = f"Plan missing required fields. Must include: {required_fields}"
            log_error(error_msg)
            raise ValueError(error_msg)

        tool_name = plan["tool"]
        parameters = plan["parameters"]
        action_uuid = str(uuid.uuid4())

        execution_event = parent_trace.span(
            name=f"tool_execution_{tool_name}",
            input={
                "tool": tool_name,
                "parameters": parameters,
                "step": plan["step"]
            },
            metadata={
                "conversation_id": self.state.conversation_uuid,
                "action_id": action_uuid
            }
        )

        try:
            if tool_name == "webscrape":
                if "url" not in parameters:
                    raise ValueError("URL parameter is required for webscrape tool")
                document = await self.web_service.scrape_url(parameters, conversation_uuid=self.state.conversation_uuid)
            elif tool_name == "translate":
                if not hasattr(self.state, 'actions') or not self.state.actions:
                    raise ValueError("No previous document available to process")
                last_doc = self.state.actions[-1].result
                document = await self.document_service.translate(parameters, last_doc, parent_trace)
            else:
                error_msg = f"Unknown tool: {tool_name}"
                log_error(error_msg)
                raise ValueError(error_msg)

            # Update event with successful execution


            log_info(f"Executing {tool_name} with parameters: {parameters}", style="bold magenta")
            log_tool_call(tool_name, parameters, document)
            
            action = Action(
                uuid=uuid.UUID(action_uuid),
                name=plan['step'],
                tool_uuid=next((tool.uuid for tool in self.state.tools if tool.name == tool_name), None),
                payload=plan["parameters"],
                result=document
            )
            self.db_service.store_action(action)
            
            if not hasattr(self.state, 'actions'):
                self.state.actions = []
            
            self.state.actions.append(action)
            self.state.documents.append(document)

            execution_event.end(
                output=document,
                level="DEFAULT",
                status_message="Tool execution successful"
            )
            
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            # Update event with error status
            execution_event.end(
                output={"error": str(e)},
                level="ERROR",
                status_message=error_msg
            )
            log_error(error_msg)
            raise Exception(error_msg)

    async def _answer(self, messages: List[Dict[str, Any]], parent_trace=None) -> str:
        try:
            # Get system prompt for final answer
            prompt = self.langfuse_service.get_prompt(
                name="agent_answer",
                prompt_type="text",
                label="latest"
            )
            0
            # Compile the prompt
            system_prompt = prompt.compile()
            
            # Get model from prompt config, fallback to default
            model = prompt.config.get("model", "gpt-4o-mini")
            
            # Create generation observation
            generation = parent_trace.generation(
                name="agent_answer",
                model=model,
                input=system_prompt,
                metadata={
                    "conversation_id": self.state.conversation_uuid
                }
            )
            
            # Get final answer from OpenAI
            final_answer = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model
            )
                        
            # Update generation with the response
            generation.end(
                output=final_answer,
            )
            
            return final_answer
            
        except Exception as e:
            raise Exception(f"Error generating final answer: {str(e)}")

