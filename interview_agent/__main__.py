"""
Main entry point for running the Interview Agent server.
"""

import uvicorn
import argparse
from .server import app

def main():
    parser = argparse.ArgumentParser(description="Run the Interview Agent server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "interview_agent.server:app",
        host=args.host,
        port=args.port,
        reload=False
    )

if __name__ == "__main__":
    main()