import unittest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from interview_agent.server import app
from interview_agent.types import InterviewState


class TestAPI(unittest.TestCase):
    """Test cases for the Interview Agent API endpoints"""
    
    def setUp(self):
        """Set up test client and sample data"""
        self.client = TestClient(app)
        self.sample_resume_content = """# John Doe
        Software Engineer
        
        ## Experience
        **Senior Software Engineer** - Tech Corp (2020-Present)
        - Developed backend services using Python and FastAPI
        - Worked with databases and cloud platforms
        
        ## Skills
        - Python, FastAPI, SQL, Docker
        """
        
    def tearDown(self):
        """Clean up after tests"""
        pass
        
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Interview Agent API is running"})
        
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
        
    @patch('interview_agent.server.parse_resume')
    @patch('interview_agent.server.create_interview_graph')
    def test_start_interview_success(self, mock_create_graph, mock_parse_resume):
        """Test successful interview start"""
        # Mock the dependencies
        mock_parse_resume.return_value = self.sample_resume_content
        mock_graph_instance = MagicMock()
        mock_create_graph.return_value.compile.return_value = mock_graph_instance
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_file:
            tmp_file.write(self.sample_resume_content.encode())
            tmp_file_path = tmp_file.name
            
        try:
            with open(tmp_file_path, "rb") as f:
                response = self.client.post(
                    "/interview/start",
                    files={"file": ("resume.md", f, "text/markdown")},
                    data={"adaptive_questioning": "true"}
                )
                
            self.assertEqual(response.status_code, 200)
            json_response = response.json()
            self.assertIn("session_id", json_response)
            self.assertIn("message", json_response)
            self.assertEqual(json_response["message"], "Interview started successfully")
            
            # Verify mocks were called
            mock_parse_resume.assert_called_once()
            mock_create_graph.assert_called_once()
            
        finally:
            os.unlink(tmp_file_path)
            
    @patch('interview_agent.server.parse_resume')
    def test_start_interview_parsing_error(self, mock_parse_resume):
        """Test interview start with parsing error"""
        # Mock parse_resume to raise an exception
        mock_parse_resume.side_effect = Exception("Parsing error")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_file:
            tmp_file.write(self.sample_resume_content.encode())
            tmp_file_path = tmp_file.name
            
        try:
            with open(tmp_file_path, "rb") as f:
                response = self.client.post(
                    "/interview/start",
                    files={"file": ("resume.md", f, "text/markdown")},
                    data={"adaptive_questioning": "true"}
                )
                
            self.assertEqual(response.status_code, 500)
            json_response = response.json()
            self.assertIn("detail", json_response)
            self.assertIn("Error starting interview", json_response["detail"])
            
        finally:
            os.unlink(tmp_file_path)
            
    @patch('interview_agent.server.interview_sessions')
    @patch('interview_agent.server.interview_graphs')
    def test_get_next_question_success(self, mock_interview_graphs, mock_interview_sessions):
        """Test getting next question successfully"""
        # Setup mock session and graph data
        session_id = "test-session-id"
        mock_state: InterviewState = {
            "messages": [],
            "resume_content": self.sample_resume_content,
            "projects": [],
            "technical_points": [],
            "interview_questions": [
                {
                    "question": "Can you tell me about your experience with Python?",
                    "follow_up_questions": [
                        "What Python frameworks have you worked with?",
                        "How do you handle performance optimization in Python?"
                    ],
                    "answers": []
                }
            ],
            "current_question_index": 0,
            "current_follow_up_index": -1,
            "coding_challenge": None,
            "coding_solution": None,
            "evaluation": None,
            "final_score": None,
            "final_feedback": None,
            "interview_stage": "questioning",
            "enable_adaptive_questioning": True
        }
        
        mock_app_graph = MagicMock()
        mock_app_graph.invoke.return_value = mock_state
        
        # Configure mocks to simulate session existence
        mock_interview_sessions.__contains__.return_value = True
        mock_interview_sessions.__getitem__.return_value = mock_state
        mock_interview_graphs.__contains__.return_value = True
        mock_interview_graphs.__getitem__.return_value = mock_app_graph
        
        response = self.client.get(f"/interview/{session_id}/question")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("session_id", json_response)
        self.assertIn("question", json_response)
        self.assertIn("question_type", json_response)
        self.assertIn("progress", json_response)
        self.assertEqual(json_response["session_id"], session_id)
            
    @patch('interview_agent.server.interview_sessions')
    def test_submit_answer_success(self, mock_interview_sessions):
        """Test submitting an answer successfully"""
        session_id = "test-session-id"
        
        # Setup mock session data
        mock_state = {
            "messages": [],
            "resume_content": self.sample_resume_content,
            "projects": [],
            "technical_points": [],
            "interview_questions": [
                {
                    "question": "Can you tell me about your experience with Python?",
                    "follow_up_questions": [],
                    "answers": []
                }
            ],
            "current_question_index": 0,
            "current_follow_up_index": -1,
            "coding_challenge": None,
            "coding_solution": None,
            "evaluation": None,
            "final_score": None,
            "final_feedback": None,
            "interview_stage": "questioning",
            "enable_adaptive_questioning": True
        }
        
        mock_interview_sessions.__contains__.return_value = True
        mock_interview_sessions.__getitem__.return_value = mock_state
        
        response = self.client.post(
            f"/interview/{session_id}/answer",
            json={"answer": "I have 5 years of Python experience."}
        )
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("session_id", json_response)
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], "Answer submitted successfully")
        
    def test_submit_answer_missing_session(self):
        """Test submitting an answer for non-existent session"""
        session_id = "non-existent-session"
        
        response = self.client.post(
            f"/interview/{session_id}/answer",
            json={"answer": "Test answer"}
        )
        
        self.assertEqual(response.status_code, 404)
        json_response = response.json()
        self.assertIn("detail", json_response)
        self.assertEqual(json_response["detail"], "Session not found")
        
    @patch('interview_agent.server.interview_sessions')
    def test_get_interview_result(self, mock_interview_sessions):
        """Test getting interview results"""
        session_id = "test-session-id"
        
        # Setup mock session data
        mock_state = {
            "messages": [],
            "resume_content": self.sample_resume_content,
            "projects": [],
            "technical_points": [],
            "interview_questions": [],
            "current_question_index": 0,
            "current_follow_up_index": -1,
            "coding_challenge": None,
            "coding_solution": None,
            "evaluation": None,
            "final_score": 85.0,
            "final_feedback": "Good technical knowledge",
            "interview_stage": "completed",
            "enable_adaptive_questioning": True
        }
        
        # Configure mocks to simulate session existence
        mock_interview_sessions.__contains__.return_value = True
        mock_interview_sessions.get.return_value = mock_state
        
        response = self.client.get(f"/interview/{session_id}/result")
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("final_score", json_response)
        self.assertIn("final_feedback", json_response)
        self.assertIn("status", json_response)
        self.assertEqual(json_response["final_score"], 85.0)
        self.assertEqual(json_response["final_feedback"], "Good technical knowledge")
        self.assertEqual(json_response["status"], "completed")
            
    def test_end_interview(self):
        """Test ending an interview session"""
        session_id = "test-session-id"
        
        # Try to delete a session (will succeed regardless of whether it exists)
        response = self.client.delete(f"/interview/{session_id}")
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertIn("message", json_response)
        self.assertEqual(json_response["message"], "Interview session ended successfully")


if __name__ == '__main__':
    unittest.main()