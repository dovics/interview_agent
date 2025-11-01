"""
Interview Agent Implementation using LangGraph

This module implements an interview agent that follows this process:
1. Accepts resume uploads (PDF, DOCX, or Markdown)
2. Parses resume to Markdown and analyzes with LLM
3. Conducts technical interviews with multi-round questioning
4. Provides a coding challenge from LeetCode
5. Scores the candidate based on responses

This version uses LangGraph to orchestrate the workflow.
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

from .parser import parse_resume

load_dotenv()

class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class TechnicalPoint:
    """Represents a technical point to be discussed in the interview"""
    name: str
    description: str

@dataclass
class Project:
    """Represents a project from the candidate's resume"""
    title: str
    description: str
    technologies: List[str]

@dataclass
class InterviewQuestion:
    """Represents a question in the interview"""
    topic: str  # Either a project title or technical point name
    question: str
    follow_up_questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)  # Store candidate's answers

@dataclass
class CodingChallenge:
    """Represents a coding challenge"""
    title: str
    description: str
    difficulty: DifficultyLevel
    solution: str

class InterviewState(TypedDict):
    """State of the interview process"""
    messages: Annotated[list, operator.add]
    resume_content: str
    projects: List[Dict[str, Any]]
    technical_points: List[Dict[str, Any]]
    interview_questions: List[Dict[str, Any]]
    current_question_index: int
    current_follow_up_index: int
    coding_challenge: Optional[Dict[str, Any]]
    coding_solution: Optional[str]
    evaluation: Optional[Dict[str, Any]]
    final_score: Optional[int]
    final_feedback: Optional[str]
    interview_stage: str  # resume_upload, resume_analysis, questioning, coding, evaluation, completed

# Node functions for the graph
def upload_resume_node(state: InterviewState) -> Dict[str, Any]:
    """Node for uploading and parsing resume"""
    # Get file path from state
    file_path = state.get("messages", [{}])[0].get("file_path") if state.get("messages") else None
    
    # If no file path provided, raise an error
    if not file_path:
        raise ValueError("No resume file path provided. Please provide a path to a PDF, DOCX, or Markdown file.")
    
    try:
        # Parse the actual file
        resume_content = parse_resume(file_path)
        
        # Check if resume content is empty
        if not resume_content or not resume_content.strip():
            raise ValueError(f"Parsed resume content is empty for file: {file_path}")
            
    except Exception as e:
        # If parsing fails, raise an error with details
        raise ValueError(f"Failed to parse resume file '{file_path}': {str(e)}")
    
    return {
        "resume_content": resume_content,
        "interview_stage": "resume_analysis"
    }

def analyze_resume_node(state: InterviewState) -> Dict[str, Any]:
    """Node for analyzing resume and extracting projects and technical points"""
    model = init_chat_model("deepseek-chat", temperature=0)
    
    prompt = f"""
    Please analyze the following resume and extract:
    1. 1-2 key projects the candidate worked on
    2. 3-4 technical skills or areas of expertise
    
    For each project, provide:
    - Title
    - Brief description
    - Technologies used
    
    For each technical point, provide:
    - Name of the technical skill
    - Brief description
    
    Format your response as JSON with this structure:
    {{
      "projects": [
        {{
          "title": "Project title",
          "description": "Brief description",
          "technologies": ["tech1", "tech2"]
        }}
      ],
      "technical_points": [
        {{
          "name": "Technical skill name",
          "description": "Brief description"
        }}
      ]
    }}
    
    Resume:
    {state['resume_content']}
    """
    
    try:
        response = model.invoke([
            SystemMessage(content="You are an expert technical recruiter."),
            HumanMessage(content=prompt)
        ])
        
        # Parse the JSON response
        parser = JsonOutputParser()
        result = parser.parse(response.content)
        
        projects = result.get("projects", [])
        technical_points = result.get("technical_points", [])
        
        return {
            "projects": projects,
            "technical_points": technical_points,
            "interview_stage": "questioning"
        }
    except Exception as e:
        raise ValueError(f"Failed to analyze resume: {str(e)}")

def generate_questions_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating interview questions"""
    model = init_chat_model("deepseek-chat", temperature=0.7)
    
    # Combine projects and technical points for question generation
    topics = []
    
    for project in state.get("projects", []):
        topics.append({
            "type": "project",
            "title": project["title"],
            "description": project["description"],
            "technologies": project["technologies"]
        })
    
    for tech_point in state.get("technical_points", []):
        topics.append({
            "type": "technical",
            "name": tech_point["name"],
            "description": tech_point["description"]
        })
    
    # Generate questions for each topic
    all_questions = []
    
    for topic in topics:
        if topic["type"] == "project":
            prompt = f"""
            Based on this project:
            Title: {topic['title']}
            Description: {topic['description']}
            Technologies: {', '.join(topic['technologies'])}
            
            Generate a main interview question and 2 follow-up questions about this project.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['title']}",
              "question": "Main question about the project",
              "follow_up_questions": [
                "Follow-up question 1",
                "Follow-up question 2"
              ]
            }}
            """
        else:  # technical point
            prompt = f"""
            Based on this technical skill:
            Name: {topic['name']}
            Description: {topic['description']}
            
            Generate a main interview question and 2 follow-up questions about this technical skill.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['name']}",
              "question": "Main question about the technical skill",
              "follow_up_questions": [
                "Follow-up question 1",
                "Follow-up question 2"
              ]
            }}
            """
        
        try:
            response = model.invoke([
                SystemMessage(content="You are an expert technical interviewer."),
                HumanMessage(content=prompt)
            ])
            
            parser = JsonOutputParser()
            questions = parser.parse(response.content)
            all_questions.append(questions)
            
        except Exception as e:
            # If we can't generate questions for one topic, continue with others
            print(f"Warning: Failed to generate questions for topic {topic}: {str(e)}")
            continue
    
    return {
        "interview_questions": all_questions,
        "current_question_index": 0,
        "current_follow_up_index": -1,  # -1 means we're on the main question
        "interview_stage": "questioning"
    }

def ask_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for presenting questions to the candidate and collecting answers"""
    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    
    if not questions or current_index >= len(questions):
        return {"interview_stage": "coding"}
    
    current_q_set = questions[current_index]
    
    # Determine which question to ask
    if follow_up_index == -1:
        # Ask main question
        question_text = current_q_set.get("question", "")
    else:
        # Ask follow-up question
        follow_ups = current_q_set.get("follow_up_questions", [])
        if follow_up_index < len(follow_ups):
            question_text = follow_ups[follow_up_index]
        else:
            question_text = ""
    
    if not question_text:
        # Move to next question set if current one doesn't have valid questions
        return {
            "current_question_index": current_index + 1,
            "current_follow_up_index": -1,
            "interview_stage": "questioning"
        }
    
    # Display the question to the candidate
    print(f"\nQuestion: {question_text}")
    print("-" * 50)
    
    # Get answer from terminal input
    answer = input("Your answer: ").strip()
    
    # Update the interview questions with the answer
    updated_questions = list(questions)
    current_q_set_copy = dict(updated_questions[current_index])
    
    # Initialize answers list if it doesn't exist
    if "answers" not in current_q_set_copy:
        current_q_set_copy["answers"] = []
    
    # Add the answer to the answers list
    current_q_set_copy["answers"].append(answer)
    updated_questions[current_index] = current_q_set_copy
    
    return {
        "interview_questions": updated_questions,
        "interview_stage": "questioning"
    }

def next_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for determining the next question to ask"""
    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    
    if not questions or current_index >= len(questions):
        return {"interview_stage": "coding"}
    
    current_q_set = questions[current_index]
    follow_ups = current_q_set.get("follow_up_questions", [])
    
    # If we're on the main question (-1) or haven't finished follow-ups, continue with follow-ups
    if follow_up_index < len(follow_ups) - 1:
        # Move to next follow-up question
        return {
            "current_follow_up_index": follow_up_index + 1,
            "interview_stage": "questioning"
        }
    # If we've finished follow-ups and there are more question sets, go to next set
    elif current_index < len(questions) - 1:
        # Move to next main question
        return {
            "current_question_index": current_index + 1,
            "current_follow_up_index": -1,  # Reset to main question
            "interview_stage": "questioning"
        }
    # Otherwise, move to coding challenge
    else:
        return {"interview_stage": "coding"}

def generate_coding_challenge_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating a coding challenge"""
    model = init_chat_model("deepseek-chat", temperature=0.5)
    
    prompt = """
    Generate a medium difficulty LeetCode-style coding challenge.
    It should be a well-known computer science problem that tests problem-solving skills.
    
    Format your response as JSON with this structure:
    {
      "title": "Problem title",
      "description": "Detailed problem description with examples",
      "difficulty": "medium",
      "solution": "Python solution code"
    }
    """
    
    try:
        response = model.invoke([
            SystemMessage(content="You are an expert in algorithms and data structures."),
            HumanMessage(content=prompt)
        ])
        
        parser = JsonOutputParser()
        challenge = parser.parse(response.content)
        
        # Ask for solution from candidate
        print(f"\nCoding Challenge: {challenge.get('title', '')}")
        print("=" * 50)
        print(f"{challenge.get('description', '')}")
        print("-" * 50)
        solution = input("Write your solution:\n").strip()
        
        return {
            "coding_challenge": challenge,
            "coding_solution": solution,
            "interview_stage": "evaluation"
        }
    except Exception as e:
        raise ValueError(f"Failed to generate coding challenge: {str(e)}")

def evaluate_responses_node(state: InterviewState) -> Dict[str, Any]:
    """Node for evaluating candidate responses"""
    model = init_chat_model("deepseek-chat", temperature=0)
    
    # Prepare the data for evaluation
    evaluation_data = {
        "resume_content": state.get("resume_content", ""),
        "projects": state.get("projects", []),
        "technical_points": state.get("technical_points", []),
        "interview_questions": state.get("interview_questions", []),
        "coding_challenge": state.get("coding_challenge", {}),
        "coding_solution": state.get("coding_solution", "")
    }
    
    prompt = f"""
    Based on the following interview data, evaluate the candidate and provide a score from 0-100 and feedback.
    
    Interview Data:
    {json.dumps(evaluation_data, indent=2)}
    
    Please provide:
    1. A score from 0-100 (where 60+ is passing, 80+ is good, 90+ is excellent)
    2. Detailed feedback explaining the score
    
    Format your response as JSON with this structure:
    {{
      "score": 85,
      "feedback": "Detailed feedback explaining the score"
    }}
    """
    
    try:
        response = model.invoke([
            SystemMessage(content="You are an expert technical interviewer and evaluator."),
            HumanMessage(content=prompt)
        ])
        
        parser = JsonOutputParser()
        evaluation = parser.parse(response.content)
        
        return {
            "evaluation": evaluation,
            "final_score": evaluation.get("score"),
            "final_feedback": evaluation.get("feedback"),
            "interview_stage": "completed"
        }
    except Exception as e:
        raise ValueError(f"Failed to evaluate responses: {str(e)}")

def route_question(state: InterviewState) -> str:
    """Route to next question or move to coding challenge"""
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    questions = state.get("interview_questions", [])
    stage = state.get("interview_stage", "")
    
    # If we're not in questioning stage, route accordingly
    if stage != "questioning":
        if stage == "coding":
            return "coding"
        elif stage == "evaluation":
            return "evaluation"
        elif stage == "completed":
            return "completed"
        return "coding"
    
    if not questions:
        return "coding"
    
    if current_index >= len(questions):
        return "coding"
    
    current_question_set = questions[current_index]
    follow_ups = current_question_set.get("follow_up_questions", [])
    
    # If we're on the main question (-1) or haven't finished follow-ups, continue questioning
    if follow_up_index < len(follow_ups) - 1:
        return "continue_questioning"
    # If we've finished follow-ups and there are more question sets, go to next set
    elif current_index < len(questions) - 1:
        return "next_question_set"
    # Otherwise, move to coding challenge
    else:
        return "coding"

# Create the interview graph
def create_interview_graph() -> StateGraph:
    """Create the interview workflow graph"""
    # Create the graph
    workflow = StateGraph(InterviewState)
    
    # Add nodes
    workflow.add_node("upload_resume", upload_resume_node)
    workflow.add_node("analyze_resume", analyze_resume_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("ask_question", ask_question_node)
    workflow.add_node("next_question", next_question_node)
    workflow.add_node("generate_coding_challenge", generate_coding_challenge_node)
    workflow.add_node("evaluate_responses", evaluate_responses_node)
    
    # Add edges
    workflow.add_edge(START, "upload_resume")
    workflow.add_edge("upload_resume", "analyze_resume")
    workflow.add_edge("analyze_resume", "generate_questions")
    
    # Add conditional edges for questioning
    workflow.add_conditional_edges(
        "generate_questions",
        route_question,
        {
            "continue_questioning": "ask_question",
            "next_question_set": "ask_question",
            "coding": "generate_coding_challenge"
        }
    )
    
    workflow.add_edge("ask_question", "next_question")
    
    workflow.add_conditional_edges(
        "next_question",
        route_question,
        {
            "continue_questioning": "ask_question",
            "next_question_set": "ask_question",
            "coding": "generate_coding_challenge"
        }
    )
    
    workflow.add_edge("generate_coding_challenge", "evaluate_responses")
    workflow.add_edge("evaluate_responses", END)
    
    return workflow

def run_interview(file_path: str) -> Dict[str, Any]:
    """Run the full interview process"""
    # Create the graph
    graph = create_interview_graph()
    app = graph.compile()
    
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
        "interview_stage": "resume_upload"
    }
    
    # Run the interview
    final_state = app.invoke(initial_state)
    
    return final_state