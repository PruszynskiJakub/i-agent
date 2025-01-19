from rich.logging import RichHandler
import logging
import json
from typing import Any, Optional
import traceback

# Configure the logger with rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("iAgent")

def log_tool_call(function_name: str, args: Any, result: Any) -> None:
    """Log a tool call with its arguments and result"""
    try:
        args_str = json.dumps(args, indent=2)
        result_str = json.dumps(result, indent=2) if result else "None"
        logger.info(f" 🛠️ Tool Call: {function_name}\nArgs: {args_str}\nResult: {result_str}")
    except Exception as e:
        log_exception(" ❌ Error logging tool call", e)

def log_error(message: str, exc_info: bool = False) -> None:
    """
    Log an error message with optional exception info
    
    Args:
        message: The error message to log
        exc_info: If True, include exception info and traceback
    """
    logger.error(message, exc_info=exc_info)

def log_exception(message: str, exc: Optional[Exception] = None) -> None:
    """
    Log an exception with full traceback
    
    Args:
        message: Context message about the error
        exc: The exception object. If None, gets current exception info
    """
    if exc is None:
        logger.exception(message)
    else:
        exc_info = (type(exc), exc, exc.__traceback__)
        logger.error(f"{message}: {str(exc)}", exc_info=exc_info)

def log_info(message: str) -> None:
    """Log an info message"""
    logger.info(message)
