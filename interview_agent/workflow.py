"""
Workflow definition for the Interview Agent.

This module contains the workflow definition using LangGraph.
"""

from langgraph.graph import StateGraph, START, END

from .types import InterviewState
from .nodes import (
    analyze_resume_node,
    generate_questions_node,
    ask_question_node,
    analyze_response_quality_node,
    generate_adaptive_questions_node,
    next_question_node,
    generate_coding_challenge_node,
    evaluate_responses_node
)
from .routing import route_question


def create_interview_graph() -> StateGraph:
    """Create the interview workflow graph"""
    # Create the graph
    workflow = StateGraph(InterviewState)
    
    # Add nodes
    workflow.add_node("analyze_resume", analyze_resume_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("ask_question", ask_question_node)
    workflow.add_node("analyze_response_quality", analyze_response_quality_node)
    workflow.add_node("generate_coding_challenge", generate_coding_challenge_node)
    workflow.add_node("generate_adaptive_questions", generate_adaptive_questions_node)
    workflow.add_node("next_question", next_question_node)
    workflow.add_node("evaluate_responses", evaluate_responses_node)
    
    # Add edges
    workflow.add_edge(START, "analyze_resume")
    workflow.add_edge("analyze_resume", "generate_questions")
    workflow.add_edge("generate_questions", "generate_coding_challenge")
    # Add conditional edges for questioning
    workflow.add_conditional_edges(
        "generate_coding_challenge",
        route_question,
        {
            "next_question_set": "ask_question",
            "adaptive_questioning": "generate_adaptive_questions",
            "evaluation": "evaluate_responses",
        }
    )

    workflow.add_edge("ask_question", "analyze_response_quality")
    
    workflow.add_conditional_edges(
        "analyze_response_quality",
        route_question,
        {
            "next_question_set": "next_question",
            "adaptive_questioning": "generate_adaptive_questions",
            "evaluation": "evaluate_responses",
        }
    )
    
    workflow.add_edge("generate_adaptive_questions", "ask_question")
    
    workflow.add_conditional_edges(
        "next_question",
        route_question,
        {
            "next_question_set": "ask_question",
            "adaptive_questioning": "analyze_response_quality",
            "evaluation": "evaluate_responses",
        }
    )
    
    workflow.add_edge("evaluate_responses", END)
    
    return workflow