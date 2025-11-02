#!/usr/bin/env python3
"""
Main entry point for the Interview Agent.
This script allows users to run the interview agent from the command line.
"""

import argparse
import sys
import os
from pathlib import Path

from interview_agent.core import run_interview
from interview_agent.parser import parse_resume
from interview_agent import set_log_level


def main():
    """Main function to run the interview agent from command line"""
    parser = argparse.ArgumentParser(
        description="Interview Agent - Conducts technical interviews based on resumes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py example_resume.md
  python main.py /path/to/resume.pdf
  python main.py resume.docx --output results.json
  python main.py --server --port 8000
        """
    )
    
    parser.add_argument(
        "resume_path",
        nargs='?',
        help="Path to the resume file (PDF, DOCX, or Markdown)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file to save results (JSON format)",
        type=str
    )
    
    parser.add_argument(
        "--log-level",
        "-l",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR)",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        type=str
    )
    
    parser.add_argument(
        "--no-adaptive-questioning",
        help="Disable adaptive questioning based on user responses",
        action="store_true"
    )
    
    parser.add_argument(
        "--server",
        help="Start HTTP server instead of command line interface",
        action="store_true"
    )
    
    parser.add_argument(
        "--host",
        help="Host to bind the server to",
        default="127.0.0.1",
        type=str
    )
    
    parser.add_argument(
        "--port",
        help="Port to bind the server to",
        default=8000,
        type=int
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    set_log_level(args.log_level)
    
    # Start HTTP server if requested
    if args.server:
        start_server(args.host, args.port)
        return
    
    # Validate resume path
    if not args.resume_path:
        print("Error: Resume file path is required when not running in server mode.")
        parser.print_help()
        sys.exit(1)
        
    resume_path = Path(args.resume_path)
    if not resume_path.exists():
        print(f"Error: Resume file '{args.resume_path}' does not exist.")
        sys.exit(1)
    
    if not resume_path.is_file():
        print(f"Error: '{args.resume_path}' is not a file.")
        sys.exit(1)
    
    try:
        print(f"Starting interview with resume: {resume_path}")
        if args.no_adaptive_questioning:
            print("Adaptive questioning is disabled.")
        print("=" * 60)
        
        # Parse resume before starting the interview workflow
        resume_content = parse_resume(str(resume_path))
        
        # Run the interview
        result = run_interview(resume_content, not args.no_adaptive_questioning)
        
        # Display results
        print("\n" + "=" * 60)
        print("INTERVIEW RESULTS")
        print("=" * 60)
        print(f"Final Score: {result.get('final_score', 'N/A')}/100")
        print(f"Feedback: {result.get('final_feedback', 'N/A')}")
        
        # Save to output file if specified
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to: {args.output}")
            
    except KeyboardInterrupt:
        print("\n\nInterview interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running interview: {e}")
        sys.exit(1)


def start_server(host: str, port: int):
    """Start the HTTP server"""
    print(f"Starting Interview Agent HTTP server on {host}:{port}")
    
    try:
        import uvicorn
        from interview_agent.server import app
        uvicorn.run(app, host=host, port=port)
    except ImportError as e:
        print(f"Error: Missing dependencies for HTTP server. Please install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()