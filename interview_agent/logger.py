import logging
import os
from typing import Any, Dict
from functools import wraps

# 创建日志记录器
logger = logging.getLogger('interview_agent')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(console_handler)

def set_log_level(level: str):
    """
    设置日志级别
    
    Args:
        level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
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
    记录工具调用
    
    Args:
        tool_name: 工具名称
        args: 工具参数
        result: 工具返回结果
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {args}")
        logger.debug(f"Result: {result}")
    else:
        logger.info(f"Executed tool: {tool_name}")

def log_llm_call(model_name: str, prompt: str, response: str):
    """
    记录LLM调用
    
    Args:
        model_name: 模型名称
        prompt: 提示词
        response: 模型响应
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"LLM call: {model_name}")
        logger.debug(f"Prompt: {prompt}")
        logger.debug(f"Response: {response}")
    else:
        logger.info(f"Called LLM: {model_name}")

def log_node_execution(node_name: str, input_state: Dict[str, Any], output_state: Dict[str, Any]):
    """
    记录节点执行
    
    Args:
        node_name: 节点名称
        input_state: 输入状态
        output_state: 输出状态
    """
    logger.info(f"Executing node: {node_name}")
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Input state: {input_state}")
        logger.debug(f"Output state: {output_state}")

def logged_tool(tool_func):
    """
    装饰器：为工具函数添加日志记录
    
    Args:
        tool_func: 工具函数
    """
    @wraps(tool_func)
    def wrapper(*args, **kwargs):
        tool_name = tool_func.__name__
        
        # 记录输入
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling tool {tool_name} with args: {args}, kwargs: {kwargs}")
        
        # 执行工具
        try:
            result = tool_func(*args, **kwargs)
            
            # 记录结果
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
    装饰器：为LLM调用添加日志记录
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 执行函数
        result = func(*args, **kwargs)
        
        # 记录LLM调用信息
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"LLM call args: {args}")
            logger.debug(f"LLM call kwargs: {kwargs}")
            logger.debug(f"LLM response: {result}")
        else:
            # 只记录基本信息
            if args and hasattr(args[0], '__class__'):
                model_name = args[0].__class__.__name__
                logger.info(f"Called LLM: {model_name}")
        
        return result
    return wrapper