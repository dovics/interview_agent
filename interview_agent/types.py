"""
Type definitions for the Interview Agent.

This module contains all the type definitions used in the interview agent.
"""

from typing import List, Dict, Any, Annotated, Optional
from typing_extensions import TypedDict
from dataclasses import dataclass, field
from enum import Enum
import operator
from dotenv import load_dotenv

load_dotenv()

class DifficultyLevel(Enum):
    """Difficulty levels for coding challenges"""
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
    response_analysis: List[Any] = field(default_factory=list)

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
    should_ask_follow_up: bool
    current_follow_up_index: int

    evaluation: Optional[Dict[str, Any]]
    final_score: Optional[int]
    final_feedback: Optional[str]
    interview_stage: str  # resume_upload, resume_analysis, questioning, coding, evaluation, completed
    enable_adaptive_questioning: bool  # Control whether to enable adaptive questioning
    mode: str  # Run mode: "server" or "cli"