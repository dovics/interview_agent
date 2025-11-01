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
        """
    )
    
    parser.add_argument(
        "resume_path",
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
    
    args = parser.parse_args()
    
    # 设置日志级别
    set_log_level(args.log_level)
    
    # Validate resume path
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
        
        # Run the interview
        result = run_interview(str(resume_path), not args.no_adaptive_questioning)
        
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


if __name__ == "__main__":
    main()