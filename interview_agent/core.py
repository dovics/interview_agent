"""
Main entry point for the Interview Agent core functionality.

This module provides the main interface for running the interview agent.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

from .workflow import create_interview_graph
from .logger import set_log_level

load_dotenv()

# 从环境变量获取日志级别，如果没有设置则默认为INFO
log_level = os.getenv("LOG_LEVEL", "INFO")
set_log_level(log_level)

def run_interview(resume_content: str, enable_adaptive_questioning: bool = True) -> Dict[str, Any]:
    """Run the full interview process"""
    # Create the graph
    graph = create_interview_graph()
    # Increase recursion limit to prevent the RecursionError
    app = graph.compile(checkpointer=None, interrupt_before=None, interrupt_after=None)
    
    # Initial state
    initial_state = {
        "messages": [],
        "resume_content": resume_content,
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
        "interview_stage": "resume_analysis",
        "enable_adaptive_questioning": enable_adaptive_questioning,
        "mode": "cli"
    }
    
    # Run the interview with increased recursion limit
    final_state = app.invoke(initial_state, config={"recursion_limit": 100})
    
    return final_state
