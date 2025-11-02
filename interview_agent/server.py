"""
HTTP Server for the Interview Agent.

This module provides a FastAPI-based HTTP server to expose the interview agent
as a web service.
"""

import os
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from .workflow import create_interview_graph
from .parser import parse_resume
from .types import InterviewState


class InterviewRequest(BaseModel):
    """Request model for starting an interview"""

    adaptive_questioning: bool = True
    log_level: str = "INFO"


class InterviewStartResponse(BaseModel):
    """Response model for starting an interview"""

    session_id: str
    message: str


class QuestionResponse(BaseModel):
    """Response model for getting a question"""

    session_id: str
    question: str
    question_type: str  # "main" or "follow_up"
    progress: Dict[str, Any]  # Progress information


class AnswerRequest(BaseModel):
    """Request model for submitting an answer"""

    answer: str


class AnswerResponse(BaseModel):
    """Response model for submitting an answer"""

    session_id: str
    message: str
    next_question: Optional[str] = None
    is_finished: bool = False


class InterviewResult(BaseModel):
    """Response model for interview results"""

    final_score: Optional[float]
    final_feedback: Optional[str]
    status: str
    interview_questions: Optional[List[str]]= None
    answers: Optional[List[str]] = None
    response_analysis: Optional[List[str]] = None


# Global storage for interview sessions (in production, use Redis or a database)
interview_sessions: Dict[str, Dict[str, Any]] = {}
interview_graphs: Dict[str, Any] = {}  # Store compiled graphs

# Create FastAPI app
app = FastAPI(
    title="Interview Agent API",
    description="API for conducting technical interviews based on resumes",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Interview Agent API is running"}


@app.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(file: UploadFile, adaptive_questioning: bool = True):
    """
    Start an interview session with an uploaded resume file.

    Args:
        file: The resume file (PDF, DOCX, or Markdown)
        adaptive_questioning: Whether to enable adaptive questioning

    Returns:
        Session ID for the interview
    """
    # Generate a session ID
    session_id = str(uuid.uuid4())

    try:
        # Save uploaded file temporarily
        file_extension = Path(file.filename).suffix if file.filename else ".tmp"
        temp_file_path = f"/tmp/interview_agent_{session_id}{file_extension}"

        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse resume
        resume_content = parse_resume(temp_file_path)

        # Create interview graph
        graph = create_interview_graph()
        app_graph = graph.compile(
            checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True)),
            interrupt_before=None,
            interrupt_after=None,
        )
        interview_graphs[session_id] = app_graph

        # Initial state
        initial_state: InterviewState = {
            "messages": [{"file_path": temp_file_path}],
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
            "enable_adaptive_questioning": adaptive_questioning,
            "mode": "server",
        }

        # Store session
        interview_sessions[session_id] = initial_state

        # Clean up temporary file
        os.remove(temp_file_path)

        return InterviewStartResponse(
            session_id=session_id, message="Interview started successfully"
        )

    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        raise HTTPException(
            status_code=500, detail=f"Error starting interview: {str(e)}"
        )


@app.post("/interview/{session_id}/question", response_model=QuestionResponse)
async def get_next_question(session_id: str, answer: AnswerRequest = None):
    """
    Get the next question in the interview.

    Args:
        session_id: The session ID for the interview

    Returns:
        The next question in the interview
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_id not in interview_graphs:
        raise HTTPException(status_code=500, detail="Interview graph not found")

    try:
        # Get current state
        state = interview_sessions[session_id]
        app_graph = interview_graphs[session_id]
        if answer:
            new_state = app_graph.invoke(
                Command(resume=answer.answer),
                config={"recursion_limit": 100, "thread_id": session_id},
            )
        else:
            # Run the graph to get the next question
            new_state = app_graph.invoke(
                state, config={"recursion_limit": 100, "thread_id": session_id}
            )

        # Update session state
        interview_sessions[session_id] = new_state

        # Check if interview is completed
        if new_state["interview_stage"] == "completed":
            return QuestionResponse(
                session_id=session_id,
                question="Interview completed. Thank you!",
                question_type="main",
                progress={"status": "completed"},
            )

        # Extract question based on current stage
        question = ""
        question_type = "main"
        progress = {
            "stage": new_state["interview_stage"],
            "current_question_index": new_state["current_question_index"],
            "total_questions": (
                len(new_state["interview_questions"])
                if "interview_questions" in new_state
                else 0
            ),
        }

        if new_state["interview_stage"] in ["questioning", "adaptive_questioning"]:
            if new_state["interview_questions"]:
                current_question = new_state["interview_questions"][
                    new_state["current_question_index"]
                ]
                if new_state["current_follow_up_index"] >= 0:
                    # Follow-up question
                    question = current_question["follow_up_questions"][
                        new_state["current_follow_up_index"]
                    ]
                    question_type = "follow_up"
                else:
                    # Main question
                    question = current_question["question"]
                    question_type = "main"

        elif new_state["interview_stage"] == "coding":
            if new_state["coding_challenge"]:
                question = f"Coding Challenge: {new_state['coding_challenge']['title']}\n{new_state['coding_challenge']['description']}"
                question_type = "coding"

        return QuestionResponse(
            session_id=session_id,
            question=question,
            question_type=question_type,
            progress=progress,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting next question: {str(e)}"
        )


@app.get("/interview/{session_id}/result", response_model=InterviewResult)
async def get_interview_result(session_id: str):
    """
    Get the final result of the interview.

    Args:
        session_id: The session ID for the interview

    Returns:
        Final interview results
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Get final state
        state = interview_sessions[session_id]

        # If interview is not completed yet, run it to completion
        if state["interview_stage"] != "completed" and session_id in interview_graphs:
            return InterviewResult(
                final_score=None,
                final_feedback=None,
                status="in_progress",
                interview_questions=None,
                response_analysis=None,
            )

        questions = state.get("interview_questions", [])
        # Extract interview questions and response analysis
        interview_questions = []
        response_analysis = []
        answers = []
        # Collect response analysis from each question
        for question in questions:
            if "response_analysis" in question:
                response_analysis.extend(question["response_analysis"])
            interview_questions.append(question["question"])
            if "follow_up_questions" in question:
                interview_questions.extend(question["follow_up_questions"])
            if "answers" in question:
                answers.append(question["answers"])

        return InterviewResult(
            final_score=state.get("final_score"),
            final_feedback=state.get("final_feedback"),
            status=(
                "completed"
                if state["interview_stage"] == "completed"
                else "in_progress"
            ),
            interview_questions=interview_questions,
            answers=answers,
            response_analysis=response_analysis,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting interview result: {str(e)}"
        )


@app.delete("/interview/{session_id}")
async def end_interview(session_id: str):
    """
    End the interview session and clean up resources.

    Args:
        session_id: The session ID for the interview
    """
    if session_id in interview_sessions:
        del interview_sessions[session_id]

    if session_id in interview_graphs:
        del interview_graphs[session_id]

    return {"message": "Interview session ended successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
