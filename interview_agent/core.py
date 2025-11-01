"""
Main entry point for the Interview Agent core functionality.

This module provides the main interface for running the interview agent.
"""

import json
import os
from typing import List, Dict, Any, Annotated, Optional, Tuple
import sys
from typing_extensions import TypedDict
from dataclasses import dataclass, field
from enum import Enum
import operator
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

from .workflow import create_interview_graph
from .logger import set_log_level

load_dotenv()

# 从环境变量获取日志级别，如果没有设置则默认为INFO
log_level = os.getenv("LOG_LEVEL", "INFO")
set_log_level(log_level)

def run_interview(file_path: str, enable_adaptive_questioning: bool = True) -> Dict[str, Any]:
    """Run the full interview process"""
    # Create the graph
    graph = create_interview_graph()
    # Increase recursion limit to prevent the RecursionError
    app = graph.compile(checkpointer=None, interrupt_before=None, interrupt_after=None)
    
    # Initial state
    initial_state = {
        "messages": [{"file_path": file_path}],
        "resume_content": "",
        "projects": [],
        "technical_points": [],
        "interview_questions": [],
        "current_question_index": 0,
        "current_follow_up_index": -1,
        "coding_challenge": None,
        "coding_solution": None,
        "evaluation": None,
        "final_score": None,
        "final_feedback": None,
        "interview_stage": "resume_upload",
        "enable_adaptive_questioning": enable_adaptive_questioning  # 添加新参数到状态中
    }
    
    # Run the interview with increased recursion limit
    final_state = app.invoke(initial_state, config={"recursion_limit": 100})
    
    return final_state
