import json
from typing import List, Dict, Any
import uuid
from modules.logging_service import log_info, log_error, log_tool_call
from modules.openai_service import OpenAIService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangfuseService
from modules.web_service import WebService
from modules.document_service import DocumentService
from modules.file_service import FileService
from modules.types import ActionResult, ActionStatus, State, Action
from modules.utils import format_actions_for_prompt, format_tools_for_prompt

class AgentService:
    def __init__(self, state: State, openai_service: OpenAIService, db_service: DatabaseService, 
                 langfuse_service: LangfuseService, web_service: WebService, document_service: DocumentService,
                 file_service: FileService):
        self.state = state
        self.tool_handlers = {
            "webscrape": self._handle_webscrape,
            "translate": self._handle_translate,
            "upload": self._handle_upload,
            "open_file": self._handle_open_file
        }
        self.openai_service = openai_service
        self.db_service = db_service
        self.langfuse_service = langfuse_service
        self.web_service = web_service
        self.document_service = document_service
        self.file_service = file_service

    async def run(self, parent_trace=None) -> str:
        self._store_message(self.state.messages[-1]['content'], "user")

        await self._loop(parent_trace)
        final_answer = await self._answer(parent_trace)

        self._store_message(final_answer, "assistant")
        
        return final_answer
    
    def _store_message(self, message: str, role: str):
        self.db_service.store_message(self.state.conversation_uuid, role, message)

    async def _loop(self, parent_trace=None):
       while self.state.config["current_step"] < self.state.config["max_steps"]:
            # Plan phase
            plan_result = await self._plan(parent_trace)
            
            # If the tool is final_answer, return empty string
            if plan_result["tool"] == "final_answer":
                break
                
            # Execute phase
            await self._execute(plan_result, parent_trace)
            
            # Increment step counter at end of loop
            self.state.config["current_step"] += 1

    async def _plan(self, parent_trace=None) -> Dict[str, Any]:
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
            # Get the appropriate handler for the tool
            handler = self.tool_handlers.get(tool_name)
            if not handler:
                raise ValueError(f"Unknown tool: {tool_name}")

            # Execute the tool handler
            result = await handler(parameters)
            
            log_info(f"Executing {tool_name} with parameters: {parameters}", style="bold magenta")
            log_tool_call(tool_name, parameters, result)
            
            action = Action(
                uuid=uuid.UUID(action_uuid),
                name=plan['step'],
                tool_uuid=next((tool.uuid for tool in self.state.tools if tool.name == tool_name), None),
                payload=plan["parameters"],
                result=result.result,
                status=result.status,
                documents=result.documents
            )
            self.db_service.store_action(action)
            
            if not hasattr(self.state, 'actions'):
                self.state.actions = []
            
            self.state.actions.append(action)
            self.state.documents.extend(result.documents)

            execution_event.end(
                output=result,
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

    async def _handle_webscrape(self, parameters: Dict[str, Any]) -> ActionResult:
        if "url" not in parameters:
            raise ValueError("URL parameter is required for webscrape tool")
        return await self.web_service.scrape_url(parameters, conversation_uuid=self.state.conversation_uuid)

    async def _handle_translate(self, parameters: Dict[str, Any]) -> ActionResult:
        if not hasattr(self.state, 'actions') or not self.state.actions:
            raise ValueError("No previous document available to process")
        last_doc = self.state.actions[-1].documents[0]
        return await self.document_service.translate(parameters, last_doc)

    async def _handle_upload(self, parameters: Dict[str, Any]) -> ActionResult:
        if not hasattr(self.state, 'actions') or not self.state.actions:
            raise ValueError("No previous document available to upload")
        last_doc = self.state.actions[-1].documents[0]
        return self.file_service.upload(last_doc)

    async def _handle_open_file(self, parameters: Dict[str, Any]) -> ActionResult:
        if not hasattr(self.state, 'actions') or not self.state.actions:
            raise ValueError("No previous document available to open")
        last_doc = self.state.actions[-1].documents[0]
        return self.file_service.open_file(last_doc)

    async def _answer(self, parent_trace=None) -> str:
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
                    *self.state.messages
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

