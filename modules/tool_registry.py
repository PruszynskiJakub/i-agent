from typing import Dict, Any, Callable
from modules.types import ActionResult

class ToolRegistry:
    def __init__(self, web_service, document_service, file_service):
        self.web_service = web_service
        self.document_service = document_service
        self.file_service = file_service
        self._handlers = {
            "webscrape": self._handle_webscrape,
            "translate": self._handle_translate,
            "upload": self._handle_upload,
            "open_file": self._handle_open_file
        }

    def get_handler(self, tool_name: str) -> Callable:
        handler = self._handlers.get(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")
        return handler

    async def _handle_webscrape(self, parameters: Dict[str, Any], state) -> ActionResult:
        if "url" not in parameters:
            raise ValueError("URL parameter is required for webscrape tool")
        return await self.web_service.scrape_url(parameters, conversation_uuid=state.conversation_uuid)

    async def _handle_translate(self, parameters: Dict[str, Any], state) -> ActionResult:
        if not hasattr(state, 'actions') or not state.actions:
            raise ValueError("No previous document available to process")
        last_doc = state.actions[-1].documents[0]
        return await self.document_service.translate(parameters, last_doc)

    async def _handle_upload(self, parameters: Dict[str, Any], state) -> ActionResult:
        if not hasattr(state, 'actions') or not state.actions:
            raise ValueError("No previous document available to upload")
        last_doc = state.actions[-1].documents[0]
        return self.file_service.upload(last_doc)

    async def _handle_open_file(self, parameters: Dict[str, Any], state) -> ActionResult:
        if not hasattr(state, 'actions') or not state.actions:
            raise ValueError("No previous document available to open")
        last_doc = state.actions[-1].documents[0]
        return self.file_service.open_file(last_doc)
