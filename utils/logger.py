from rich.logging import RichHandler
import logging
import json
from typing import Any

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
        logger.error(f" ❌ Error logging tool call: {str(e)}")

def log_error(message: str) -> None:
    """Log an error message"""
    logger.error(message)

def log_info(message: str) -> None:
    """Log an info message"""
    logger.info(message)
