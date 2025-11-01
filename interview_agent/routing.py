"""
Routing functions for the Interview Agent.

This module contains all the routing logic used in the interview agent workflow.
"""

from .types import InterviewState


def route_question(state: InterviewState) -> str:
    """Route to next question or move to coding challenge"""
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    questions = state.get("interview_questions", [])
    stage = state.get("interview_stage", "")
    enable_adaptive_questioning = state.get("enable_adaptive_questioning", True)  # 获取参数
    
    # If we're not in questioning stage, route accordingly
    if stage != "questioning":
        if stage == "coding":
            return "coding"
        elif stage == "evaluation":
            return "evaluation"
        elif stage == "completed":
            return "completed"
        return "coding"
    
    # If we have no questions, go to coding
    if not questions:
        return "coding"
    
    # If we've gone through all questions, go to coding
    if current_index >= len(questions):
        return "coding"
    
    current_question_set = questions[current_index]
    follow_ups = current_question_set.get("follow_up_questions", [])
    
    # Check if we need to ask an adaptive question
    answers = current_question_set.get("answers", [])
    adaptive_questions = current_question_set.get("adaptive_questions", [])
    
    # Only ask adaptive questions if:
    # 1. Adaptive questioning is enabled
    # 2. We have answers
    # 3. We have fewer adaptive questions than regular answers
    if enable_adaptive_questioning and answers and len(adaptive_questions) < len(answers):
        return "adaptive_questioning"
    
    # If we're on the main question (-1) or haven't finished follow-ups, continue questioning
    if follow_up_index < len(follow_ups) - 1:
        return "continue_questioning"
    # If we've finished follow-ups and there are more question sets, go to next set
    elif current_index < len(questions) - 1:
        return "next_question_set"
    # Otherwise, move to coding challenge
    else:
        return "coding"