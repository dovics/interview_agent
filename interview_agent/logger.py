import logging
from typing import Any, Dict
from functools import wraps

# Create logger
logger = logging.getLogger('interview_agent')
logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

def set_log_level(level: str):
    """
    Set log level
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR
    }
    
    log_level = level_map.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    console_handler.setLevel(log_level)

def log_tool_call(tool_name: str, args: Dict[str, Any], result: Any):
    """
    Log tool call
    
    Args:
        tool_name: Tool name
        args: Tool arguments
        result: Tool result
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {args}")
        logger.debug(f"Result: {result}")
    else:
        logger.info(f"Executed tool: {tool_name}")

def log_llm_call(model_name: str, prompt: str, response: str):
    """
    Log LLM call
    
    Args:
        model_name: Model name
        prompt: Prompt text
        response: Model response
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"LLM call: {model_name}")
        logger.debug(f"Prompt: {prompt}")
        logger.debug(f"Response: {response}")
    else:
        logger.info(f"Called LLM: {model_name}")

def log_node_execution(node_name: str, input_state: Dict[str, Any], output_state: Dict[str, Any]):
    """
    Log node execution
    
    Args:
        node_name: Node name
        input_state: Input state
        output_state: Output state
    """
    # Determine if it's start or end
    if output_state is None or output_state == {}:
        status = "start"
    else:
        status = "end"
    
    logger.info(f"Node {status}: {node_name}")
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Input state: {input_state}")
        if output_state is not None and output_state != {}:
            logger.debug(f"Output state: {output_state}")

def logged_tool(tool_func):
    """
    Decorator: Add logging to tool functions
    
    Args:
        tool_func: Tool function
    """
    @wraps(tool_func)
    def wrapper(*args, **kwargs):
        tool_name = tool_func.__name__
        
        # Log input
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling tool {tool_name} with args: {args}, kwargs: {kwargs}")
        
        # Execute tool
        try:
            result = tool_func(*args, **kwargs)
            
            # Log result
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Tool {tool_name} returned: {result}")
            else:
                logger.info(f"Executed tool: {tool_name}")
                
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} failed with error: {e}")
            raise
            
    return wrapper

def logged_llm_call(func):
    """
    Decorator: Add logging to LLM calls
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Execute function
        result = func(*args, **kwargs)
        
        # Log LLM call info
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"LLM call args: {args}")
            logger.debug(f"LLM call kwargs: {kwargs}")
            logger.debug(f"LLM response: {result}")
        else:
            # Log basic info only
            if args and hasattr(args[0], '__class__'):
                model_name = args[0].__class__.__name__
                logger.info(f"Called LLM: {model_name}")
        
        return result
    return wrapper