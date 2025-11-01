# Interview Agent

An AI-powered interview agent that automates the technical interview process.

## Features

1. **Resume Parsing**: Supports PDF, DOCX, and Markdown formats
2. **Resume Analysis**: Extracts key projects and technical skills
3. **Intelligent Questioning**: Generates targeted questions and follow-ups
4. **Coding Challenges**: Provides algorithmic problems (LeetCode-style)
5. **Automated Scoring**: Evaluates candidates and provides scores/feedback

## Workflow

1. Candidate uploads resume (PDF, DOCX, or Markdown)
2. System parses resume and analyzes content with LLM
3. Agent identifies 1-2 key projects and 3-4 technical areas
4. For each topic, agent asks 2-3 rounds of questions (main question + follow-ups)
5. Agent assigns medium/hard difficulty coding challenge
6. Candidate submits solution for automated review
7. System scores candidate (0-100 scale, 60+ to pass)

## Installation

```bash
pip install -e .
```

## Dependencies

- Python 3.9+
- LangChain for LLM interactions
- DeepSeek as the primary LLM
- PyPDF2 for PDF parsing
- python-docx for DOCX parsing
- LangGraph for workflow orchestration

## Testing

The project includes unit tests for core functionality. To run the tests:

### Using the test runner script:
```bash
python run_tests.py
```

### Using pytest directly:
```bash
pytest tests/
```

### Using the project script:
```bash
python -m pyproject.toml test
```

Tests cover the resume parsing functionality, including:
- Parsing different file formats (PDF, DOCX, Markdown)
- Handling unsupported file formats
- Error handling for corrupted or inaccessible files

## Usage

### Basic Implementation

```python
from interview_agent import InterviewAgent

# Initialize the agent
agent = InterviewAgent()

# Start the interview process
resume_md = agent.upload_resume("path/to/resume.pdf")
agent.analyze_resume(resume_md)
agent.prepare_questions()

# Conduct interview (in practice, this would be interactive)
# ...

# Assign coding challenge
challenge = agent.assign_coding_challenge()

# Evaluate solution
analysis = agent.evaluate_coding_solution(code_submission)

# Score the interview
score, feedback = agent.score_interview(analysis)
```

### LangGraph Implementation

```python
from run_interview_example import run_interview_with_file

# Run with a specific resume file
final_state = run_interview_with_file("path/to/resume.pdf")
```

### Running with a Real Resume File

```python
from run_interview_example import run_interview_with_file

# Run with a specific resume file
final_state = run_interview_with_file("path/to/resume.pdf")
```

The system supports three resume formats:
- **PDF files** (`.pdf`)
- **Word documents** (`.docx`)
- **Markdown files** (`.md`, `.markdown`)

If parsing fails or no file path is provided, the system will display an appropriate error message rather than using default content.

## Architecture

### Standard Implementation

The system consists of several specialized components:

- `ResumeParser`: Handles parsing of resumes in multiple formats
- `ResumeAnalyzer`: Uses LLM to extract projects and technical points
- `QuestionGenerator`: Creates initial interview questions
- `FollowUpQuestionGenerator`: Generates follow-up questions based on answers
- `CodingChallengeProvider`: Supplies coding challenges
- `CodeAnalyzer`: Reviews submitted code solutions
- `InterviewScorer`: Calculates final scores and feedback
- `InterviewAgent`: Orchestrates the entire process

### LangGraph Implementation

The LangGraph version models the interview process as a state machine:

- **States**: Defined in `InterviewState` TypedDict
- **Nodes**: Each major step in the interview process
- **Edges**: Transitions between states based on conditions
- **Workflow**: 
  1. `upload_resume` → `analyze_resume`
  2. `analyze_resume` → questioning loop (`ask_question`)
  3. Questioning loop → `assign_coding_challenge`
  4. `assign_coding_challenge` → `evaluate`
  5. `evaluate` → END

## Error Handling

The system handles various error conditions gracefully:

1. **Missing File Path**: If no file path is provided, an error message is displayed
2. **Parsing Errors**: If the resume file cannot be parsed, a descriptive error is shown
3. **Empty Content**: If the parsed content is empty, an appropriate error is raised

## Future Improvements

- Integration with actual LeetCode API
- More sophisticated scoring algorithms
- Voice-based interviews
- Video interview capabilities
- Enhanced resume parsing with layout preservation
- Real-time interaction with human interviewers
- Customizable question generation based on job roles