from typing import Dict, List
from uuid import uuid4

from models.document import Document, DocumentType


async def _process_file(params: Dict, span) -> List[Document]:
    """Process a file and create a document from it
    
    Args:
        params: Parameters including file path and metadata
        span: Tracing span
        
    Returns:
        List[Document]: The created document
    """
    # Extract parameters
    file_path = params.get("file_path")
    if not file_path:
        raise ValueError("file_path is required")

    # Read file content
    with open(file_path, 'r') as f:
        content = f.read()

    # Create document
    doc = Document(
        uuid=uuid4(),
        type=DocumentType.FILE,
        content=content,
        metadata={
            "file_path": file_path,
            "file_name": file_path.split("/")[-1]
        }
    )

    return [doc]
