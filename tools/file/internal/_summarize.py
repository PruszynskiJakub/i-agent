from typing import Dict, List
from uuid import uuid4

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document


async def _summarize(params: Dict, span) -> List[Document]:
    """Summarize a file and create a document from it
    
    Args:
        params: Parameters including file path and metadata
        span: Tracing span
        
    Returns:
        Document: The created document
    """
    try:
        # Extract parameters
        file_path = params.get("file_path")
        if not file_path:
            create_event(span, "summarize_file", input=params, output="No file path provided")
            raise ValueError("file_path is required")

        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()

        create_event(span, "summarize_file", input=params, output={"status": "success", "file": file_path})

        # Create document
        return [create_document(
            text=content,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "file",
                "name": file_path.split("/")[-1],
                "description": f"Summarized file: {file_path}",
                "type": DocumentType.FILE,
                "file_path": file_path
            }
        )]

    except Exception as error:
        create_event(span, "process_file", level="ERROR", input=params, output={"error": str(error)})
        raise
