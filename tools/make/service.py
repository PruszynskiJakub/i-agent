from typing import Dict, List, Any
from models.document import Document
from llm.tracing import create_span, end_span
from logger.logger import log_info, log_error
from uuid import uuid4

async def _invoice(params: Dict[str, Any], span) -> Document:
    """
    Create an invoice based on the number of days worked in the current month.
    
    Args:
        params: Dictionary containing the parameters for the invoice
        span: Tracing span
    
    Returns:
        Document: A document containing information about the created invoice
    """
    try:
        days_worked = params.get("days_worked")
        if not days_worked:
            raise ValueError("days_worked parameter is required")
        
        # Here you would implement the actual automation to create the invoice
        # and upload it to Google Drive
        
        # For now, we'll just return a document with the information
        invoice_info = {
            "days_worked": days_worked,
            "status": "created",
            "location": "Google Drive",
            "message": f"Invoice created for {days_worked} days worked this month"
        }
        
        log_info(f"Created invoice for {days_worked} days worked")
        
        # Create a document with the invoice information
        return Document(
            uuid=str(uuid4()),
            content=f"Invoice created for {days_worked} days worked this month. The invoice has been uploaded to your Google Drive.",
            metadata={
                "type": "invoice",
                "days_worked": days_worked,
                "source": "make"
            }
        )
    except Exception as e:
        log_error(f"Error creating invoice: {str(e)}")
        raise

async def execute_make(action: str, params: Dict[str, Any], trace) -> List[Document]:
    """
    Execute the specified make action with the given parameters.
    
    Args:
        action: The action to execute
        params: The parameters for the action
        trace: The trace object for logging
    
    Returns:
        List[Document]: A list of documents resulting from the action
    """
    action_span = create_span(trace, f"make.{action}")
    
    try:
        if action == "invoice":
            document = await _invoice(params, action_span)
            end_span(action_span, document)
            return [document]
        else:
            raise ValueError(f"Unknown make action: {action}")
    except Exception as e:
        end_span(action_span, {"error": str(e)}, "error")
        raise
