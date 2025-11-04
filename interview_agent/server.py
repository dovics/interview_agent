"""
HTTP Server for the Interview Agent.

This module provides a FastAPI-based HTTP server to expose the interview agent
as a web service.
"""

import os
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
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
    interview_questions: Optional[List[str]] = None
    answers: Optional[List[str]] = None
    response_analysis: Optional[List[str]] = None


class Server:
    """Server class to manage interview sessions and graphs"""
    
    def __init__(self):
        """Initialize the server with empty session and graph storage"""
        self.interview_sessions: Dict[str, Dict[str, Any]] = {}
        self.interview_graphs: Dict[str, Any] = {}
        
    def create_app_graph(self, session_id: str):
        """Create and store an app graph for a session"""
        graph = create_interview_graph()
        app_graph = graph.compile(
            checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True)),
            interrupt_before=None,
            interrupt_after=None,
        )
        self.interview_graphs[session_id] = app_graph
        return app_graph
        
    def get_app_graph(self, session_id: str):
        """Retrieve an app graph for a session"""
        return self.interview_graphs.get(session_id)
        
    def remove_session(self, session_id: str):
        """Remove a session and its associated graph"""
        if session_id in self.interview_sessions:
            del self.interview_sessions[session_id]
            
        if session_id in self.interview_graphs:
            del self.interview_graphs[session_id]


# Global storage for interview sessions (in production, use Redis or a database)
server = Server()

# Create FastAPI app
app = FastAPI(
    title="Interview Agent API",
    description="API for conducting technical interviews based on resumes",
    version="1.0.0",
)

apiV1 = APIRouter(prefix='/api/v1') 
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

apiV1 = APIRouter(prefix="/api/v1")


# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {"message": "Interview Agent API is running"}


@apiV1.post("/interview/start", response_model=InterviewStartResponse)
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
        server.interview_sessions[session_id] = initial_state

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


@apiV1.post("/interview/{session_id}/question", response_model=QuestionResponse)
async def get_next_question(session_id: str, answer: AnswerRequest = None):
    """
    Get the next question in the interview.

    Args:
        session_id: The session ID for the interview

    Returns:
        The next question in the interview
    """
    if session_id not in server.interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if not server.get_app_graph(session_id):
        raise HTTPException(status_code=500, detail="Interview graph not found")

    try:
        # Get current state
        state = server.interview_sessions[session_id]
        app_graph = server.get_app_graph(session_id)
        is_interrupted = state.get("__interrupt__", None) != None
        if is_interrupted:
            if answer is not None and answer.answer != "":
                new_state = app_graph.invoke(
                    Command(resume=answer.answer),
                    config={"recursion_limit": 100, "thread_id": session_id},
                )
            else:
                new_state = state
        else:
            # Run the graph to get the next question
            new_state = app_graph.invoke(
                state, config={"recursion_limit": 100, "thread_id": session_id}
            )

        # Update session state
        server.interview_sessions[session_id] = new_state

        # Check if interview is completed
        if new_state["interview_stage"] == "completed":
            return QuestionResponse(
                session_id=session_id,
                question="Interview completed. Thank you!",
                question_type="main",
                progress={"stage": "completed"},
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


@apiV1.get("/interview/{session_id}/result", response_model=InterviewResult)
async def get_interview_result(session_id: str):
    """
    Get the final result of the interview.

    Args:
        session_id: The session ID for the interview

    Returns:
        Final interview results
    """
    if session_id not in server.interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Get final state
        state = server.interview_sessions[session_id]

        # If interview is not completed yet, run it to completion
        if state["interview_stage"] != "completed" and server.get_app_graph(session_id):
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
                answers.extend(question["answers"])

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


@apiV1.delete("/interview/{session_id}")
async def end_interview(session_id: str):
    """
    End the interview session and clean up resources.

    Args:
        session_id: The session ID for the interview
    """
    server.remove_session(session_id)

    return {"message": "Interview session ended successfully"}


@apiV1.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

app.include_router(apiV1)

# Serve frontend static files
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
print(f"Serving frontend from {frontend_build_path}")
if frontend_build_path.exists():
    # Mount static files directory
    if (frontend_build_path / "static").exists():
        app.mount("/static", StaticFiles(directory=frontend_build_path / "static"), name="static")
    
    # Serve index.html for root path
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def serve_frontend():
        try:
            with open(frontend_build_path / "index.html", "r") as file:
                return HTMLResponse(content=file.read(), status_code=200)
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Frontend build not found</h1>", status_code=404)
    
    # Serve manifest.json
    @app.get("/manifest.json", include_in_schema=False)
    async def serve_manifest():
        if (frontend_build_path / "manifest.json").exists():
            return FileResponse(frontend_build_path / "manifest.json")
        return {"message": "Manifest not found"}
else:
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"message": "Interview Agent API is running", "path": frontend_build_path}
