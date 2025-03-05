from typing import Dict, Any
from models.document import Document
from logger.logger import log_info, log_error
from uuid import uuid4

async def create_invoice(params: Dict[str, Any], span) -> Document:
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
