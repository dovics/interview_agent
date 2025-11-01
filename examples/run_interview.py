#!/usr/bin/env python3
"""
Example script demonstrating how to use the Interview Agent.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interview_agent.core import run_interview

def main():
    """Run an example interview"""
    # You would replace this with an actual resume file path
    resume_path = "examples/resume.md"
    
    if not os.path.exists(resume_path):
        print(f"Example resume not found at {resume_path}")
        print("Please provide a path to a resume file (PDF, DOCX, or Markdown)")
        return 1
    
    try:
        print(f"Running interview with resume: {resume_path}")
        result = run_interview(resume_path)
        
        print("\n" + "="*50)
        print("INTERVIEW RESULTS")
        print("="*50)
        print(f"Final Score: {result.get('final_score', 'N/A')}/100")
        print(f"Feedback: {result.get('final_feedback', 'N/A')}")
        return 0
    except Exception as e:
        print(f"Error running interview: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())