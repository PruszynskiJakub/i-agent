from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from uuid import UUID

from models.document import Document


@dataclass(frozen=True)
class ActionRecord:
    """A record of an executed tool action."""
    name: str  # e.g. "complete_task", "create_transaction"
    tool: str
    tool_uuid: Optional[UUID]
    status: str  # "SUCCESS" or "ERROR"
    input_payload: Dict[str, Any]
    output_documents: List[Document]
    step_description: str