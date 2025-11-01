# Interview Agent

An AI-powered technical interview agent that conducts interviews based on candidate resumes.

## Features

- Accepts resumes in PDF, DOCX, or Markdown format
- Parses and analyzes resumes using LLM
- Generates technical interview questions based on resume content
- Conducts multi-round questioning with follow-up questions
- Provides adaptive questioning based on candidate responses
- Offers coding challenges
- Evaluates candidates and provides scoring and feedback

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd interview-agent
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```
   
   Or if you're using Poetry:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` to add your DeepSeek API key.

## Usage

### Command Line

```bash
python main.py path/to/resume.pdf
```

Options:
- `--output`, `-o`: Save results to a JSON file
- `--log-level`, `-l`: Set logging level (DEBUG, INFO, WARNING, ERROR). Default is INFO.
- `--no-adaptive-questioning`: Disable adaptive questioning based on user responses.

Examples:
```bash
# Run with default settings
python main.py examples/resume.md

# Run with output file
python main.py resume.pdf --output interview_results.json

# Run with debug logging
python main.py resume.pdf --log-level DEBUG

# Run without adaptive questioning
python main.py resume.pdf --no-adaptive-questioning
```

### As a Module

```python
from interview_agent import run_interview

# Run with adaptive questioning (default)
result = run_interview("path/to/resume.pdf")

# Run without adaptive questioning
result = run_interview("path/to/resume.pdf", enable_adaptive_questioning=False)

print(f"Score: {result['final_score']}/100")
print(f"Feedback: {result['final_feedback']}")
```

## Logging

The system provides hierarchical logging capabilities:

- **DEBUG level**: Outputs detailed information about all tool calls and LLM calls, including inputs and outputs
- **INFO level**: Outputs basic information about executed nodes in the workflow

You can set the log level in three ways:
1. Using the command line option: `--log-level DEBUG`
2. Setting the LOG_LEVEL environment variable in `.env`
3. If neither is specified, defaults to INFO level

## How It Works

1. **Resume Upload**: Accepts and parses resume files
2. **Resume Analysis**: Uses LLM to extract projects and technical skills
3. **Question Generation**: Creates targeted interview questions
4. **Interactive Interview**: Conducts multi-round questioning
5. **Adaptive Questioning**: Generates follow-up questions based on responses (optional)
6. **Coding Challenge**: Provides a coding task
7. **Evaluation**: Scores the candidate based on all responses

## Future Improvements

- Integration with actual LeetCode API
- More sophisticated scoring algorithms
- Voice-based interviews
- Video interview capabilities
- Enhanced resume parsing with layout preservation
- Real-time interaction with human interviewers
- Customizable question generation based on job roles