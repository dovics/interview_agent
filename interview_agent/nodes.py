"""
Node functions for the Interview Agent.

This module contains all the node functions used in the interview agent workflow.
"""

import json
from typing import Dict, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.types import interrupt

from .logger import log_node_execution, log_llm_call
from .types import InterviewState


def analyze_resume_node(state: InterviewState) -> Dict[str, Any]:
    """Node for analyzing resume and extracting projects and technical points"""
    # Record node execution start
    log_node_execution("analyze_resume_node", state, {})

    model = init_chat_model("deepseek-chat", temperature=0)

    prompt = f"""
    Please analyze the following resume and extract:
    1. 1-2 key projects the candidate worked on
    2. 3-4 technical skills or areas of expertise
    
    For each project, provide:
    - Title
    - Brief description
    - Technologies used
    
    For each technical point, provide:
    - Name of the technical skill
    - Brief description
    
    Format your response as JSON with this structure:
    {{
      "projects": [
        {{
          "title": "Project title",
          "description": "Brief description",
          "technologies": ["tech1", "tech2"]
        }}
      ],
      "technical_points": [
        {{
          "name": "Technical skill name",
          "description": "Brief description"
        }}
      ]
    }}
    
    Resume:
    {state['resume_content']}
    """

    try:
        response = model.invoke(
            [
                SystemMessage(content="You are an expert technical recruiter."),
                HumanMessage(content=prompt),
            ]
        )

        # Record LLM call
        log_llm_call("deepseek-chat", prompt, response.content)

        # Parse the JSON response
        parser = JsonOutputParser()
        result = parser.parse(response.content)

        projects = result.get("projects", [])
        technical_points = result.get("technical_points", [])

        output = {
            "projects": projects,
            "technical_points": technical_points,
            "interview_stage": "questioning",
        }

        # Record node execution end
        log_node_execution("analyze_resume_node", state, output)
        return output
    except Exception as e:
        raise ValueError(f"Failed to analyze resume: {str(e)}")


def generate_questions_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating interview questions"""
    # Record node execution start
    log_node_execution("generate_questions_node", state, {})

    model = init_chat_model("deepseek-chat", temperature=0.7)

    # Combine projects and technical points for question generation
    topics = []

    for project in state.get("projects", []):
        topics.append(
            {
                "type": "project",
                "title": project["title"],
                "description": project["description"],
                "technologies": project["technologies"],
            }
        )

    for tech_point in state.get("technical_points", []):
        topics.append(
            {
                "type": "technical",
                "name": tech_point["name"],
                "description": tech_point["description"],
            }
        )

    # Generate questions for each topic
    all_questions = []

    for topic in topics:
        if topic["type"] == "project":
            prompt = f"""
            Based on this project:
            Title: {topic['title']}
            Description: {topic['description']}
            Technologies: {', '.join(topic['technologies'])}
            
            Generate a main interview question about this project.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['title']}",
              "question": "Main question about the project"
            }}
            """
        else:  # technical point
            prompt = f"""
            Based on this technical skill:
            Name: {topic['name']}
            Description: {topic['description']}
            
            Generate a main interview question about this technical skill.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['name']}",
              "question": "Main question about the technical skill"
            }}
            """

        try:
            response = model.invoke(
                [
                    SystemMessage(content="You are an expert technical interviewer."),
                    HumanMessage(content=prompt),
                ]
            )

            # Record LLM call
            log_llm_call("deepseek-chat", prompt, response.content)

            parser = JsonOutputParser()
            questions = parser.parse(response.content)
            all_questions.append(questions)

        except Exception as e:
            # If we can't generate questions for one topic, continue with others
            print(f"Warning: Failed to generate questions for topic {topic}: {str(e)}")
            continue

    output = {
        "interview_questions": all_questions,
        "current_question_index": 0,
        "current_follow_up_index": -1,  # -1 means we're on the main question
        "interview_stage": "questioning",
    }

    # Record node execution end
    log_node_execution("generate_questions_node", state, output)
    return output


def ask_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for presenting questions to the candidate and collecting answers"""
    # Record node execution start
    log_node_execution("ask_question_node", state, {})

    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    mode = state.get("mode", "cli")  # Get run mode

    if not questions or current_index >= len(questions):
        output = {"interview_stage": "coding"}
        log_node_execution("ask_question_node", state, output)
        return output

    current_q_set = questions[current_index]

    # Determine which question to ask
    if follow_up_index == -1:
        # Ask main question
        question_text = current_q_set.get("question", "")
    else:
        # Ask follow-up question
        follow_ups = current_q_set.get("follow_up_questions", [])
        if follow_up_index < len(follow_ups):
            question_text = follow_ups[follow_up_index]
        else:
            question_text = ""

    if not question_text:
        # Move to next question set if current one doesn't have valid questions
        output = {
            "current_question_index": current_index + 1,
            "current_follow_up_index": -1,
            "interview_stage": "questioning",
        }
        log_node_execution("ask_question_node", state, output)
        return output

    # Check if we're in server mode
    if mode == "server":
        # In server mode, we don't wait for input here.
        # The question will be returned via the API and the answer will come through the API as well.
        # We just return the question information for the API to handle
        answer = interrupt({"question": question_text, "question_type": "main"})

    else:
        # Display the question to the candidate
        print(f"\nQuestion: {question_text}")
        print("-" * 50)

        # Get answer from terminal input (CLI mode)
        answer = input("Your answer: ").strip()

    # Update the interview questions with the answer
    updated_questions = list(questions)
    current_q_set_copy = dict(updated_questions[current_index])

    # Initialize answers list if it doesn't exist
    if "answers" not in current_q_set_copy:
        current_q_set_copy["answers"] = []

    # Add the answer to the answers list
    current_q_set_copy["answers"].append(answer)
    updated_questions[current_index] = current_q_set_copy

    output = {
        "interview_questions": updated_questions,
        "interview_stage": "questioning",
    }

    # Record node execution end
    log_node_execution("ask_question_node", state, output)
    return output


def generate_adaptive_questions_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating adaptive follow-up questions based on candidate's answers"""
    # Record node execution start
    log_node_execution("generate_adaptive_questions_node", state, {})

    model = init_chat_model("deepseek-chat", temperature=0.7)

    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)

    if not questions or current_index >= len(questions):
        output = {}
        log_node_execution("generate_adaptive_questions_node", state, output)
        return output

    current_q_set = questions[current_index]
    answers = current_q_set.get("answers", [])

    # Only generate adaptive questions after the candidate has provided an answer
    if not answers:
        output = {}
        log_node_execution("generate_adaptive_questions_node", state, output)
        return output

    # Get the latest answer
    latest_answer = answers[-1]
    topic = current_q_set.get("topic", "")

    # Determine the type of question (main or follow-up)
    if follow_up_index == -1:
        question_type = "main"
        original_question = current_q_set.get("question", "")
    else:
        # For follow-up questions, we need to get the correct follow-up question
        follow_ups = current_q_set.get("follow_up_questions", [])
        if follow_up_index < len(follow_ups):
            original_question = follow_ups[follow_up_index]
        else:
            original_question = ""
        question_type = "follow-up"

    prompt = f"""
    Based on the candidate's answer to a {question_type} question, generate a deeper follow-up question.
    
    Topic: {topic}
    Original Question: {original_question}
    Candidate's Answer: {latest_answer}
    
    Generate a follow-up question that either:
    1. Delves deeper into a specific aspect of their answer
    2. Expands on related knowledge
    3. Challenges their approach or solution
    
    Format your response as JSON with this structure:
    {{
      "adaptive_question": "A deeper or expanded question based on the candidate's answer"
    }}
    """

    try:
        response = model.invoke(
            [
                SystemMessage(
                    content="You are an expert technical interviewer skilled at asking deep follow-up questions."
                ),
                HumanMessage(content=prompt),
            ]
        )

        # Record LLM call
        log_llm_call("deepseek-chat", prompt, response.content)

        parser = JsonOutputParser()
        result = parser.parse(response.content)
        adaptive_question = result.get("adaptive_question", "")

    except Exception as e:
        # If we can't generate an adaptive question, continue with regular flow
        print(f"Warning: Could not generate adaptive question: {str(e)}")

        output = {}
        log_node_execution("generate_adaptive_questions_node", state, output)
        return output

    # Insert the adaptive question into follow-up questions
    updated_questions = list(questions)
    current_q_set_copy = dict(updated_questions[current_index])

    # Initialize follow_up_questions list if it doesn't exist
    if "follow_up_questions" not in current_q_set_copy:
        current_q_set_copy["follow_up_questions"] = []

    # Add adaptive question to follow-up questions
    current_q_set_copy["follow_up_questions"].append(adaptive_question)

    # Update the questions in the state
    updated_questions[current_index] = current_q_set_copy

    output = {
        "interview_questions": updated_questions,
        "current_follow_up_index": len(current_q_set_copy["follow_up_questions"]) - 1,
    }

    log_node_execution("generate_adaptive_questions_node", state, output)
    return output


def analyze_response_quality_node(state: InterviewState) -> Dict[str, Any]:
    """Node for analyzing response quality and deciding whether to ask follow-up questions"""
    # Record node execution start
    log_node_execution("analyze_response_quality_node", state, {})
    enable_adaptive_questioning = state.get("enable_adaptive_questioning", False) 
    if not enable_adaptive_questioning:
        output = {}
        log_node_execution("analyze_response_quality_node", state, output)
        return output

    model = init_chat_model("deepseek-chat", temperature=0)

    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)

    if not questions or current_index >= len(questions):
        output = {}
        log_node_execution("analyze_response_quality_node", state, output)
        return output

    current_q_set = questions[current_index]
    answers = current_q_set.get("answers", [])

    # Only analyze response quality after the candidate has provided an answer
    if not answers:
        output = {}
        log_node_execution("analyze_response_quality_node", state, output)
        return output

    # Get the latest answer
    latest_answer = answers[-1]
    topic = current_q_set.get("topic", "")

    # Determine the type of question (main or follow-up)
    follow_up_index = state.get("current_follow_up_index", -1)
    if follow_up_index == -1:
        question_type = "main"
        original_question = current_q_set.get("question", "")
    else:
        # For follow-up questions, we need to get the correct follow-up question
        follow_ups = current_q_set.get("follow_up_questions", [])
        if follow_up_index < len(follow_ups):
            original_question = follow_ups[follow_up_index]
        else:
            original_question = ""
        question_type = "follow-up"

    prompt = f"""
    Analyze the candidate's answer and determine if a follow-up question is needed.
    
    Topic: {topic}
    Question Type: {question_type}
    Original Question: {original_question}
    Candidate's Answer: {latest_answer}
    
    Evaluate the answer on these criteria:
    1. Is the answer complete and detailed?
    2. Does it demonstrate understanding of the topic?
    3. Does it address the core of the question?
    
    Based on your analysis, decide if a follow-up question is warranted:
    - If the answer shows strong understanding and is comprehensive, no follow-up is needed
    - If the answer is vague, incomplete, or demonstrates lack of knowledge, a follow-up is needed
    - If the candidate refuses to answer or says they don't know, no follow-up is needed
    
    Format your response as JSON with this structure:
    {{
      "should_ask_follow_up": true/false,
      "reasoning": "Explanation for your decision"
    }}
    """

    try:
        response = model.invoke(
            [
                SystemMessage(
                    content="You are an expert technical interviewer skilled at evaluating response quality."
                ),
                HumanMessage(content=prompt),
            ]
        )

        # Record LLM call
        log_llm_call("deepseek-chat", prompt, response.content)

        parser = JsonOutputParser()
        result = parser.parse(response.content)
        should_ask_follow_up = result.get("should_ask_follow_up", False)
        reasoning = result.get("reasoning", "")

        # Store the analysis in the state
        updated_questions = list(questions)
        current_q_set_copy = dict(updated_questions[current_index])

        # Initialize response_analysis list if it doesn't exist
        if "response_analysis" not in current_q_set_copy:
            current_q_set_copy["response_analysis"] = []

        # Add analysis to the set
        current_q_set_copy["response_analysis"].append(
            {
                "answer": latest_answer,
                "should_ask_follow_up": should_ask_follow_up,
                "reasoning": reasoning,
            }
        )

        updated_questions[current_index] = current_q_set_copy

        output = {
            "interview_questions": updated_questions,
            "should_ask_follow_up": should_ask_follow_up,
        }

    except Exception as e:
        # If we can't analyze the response quality, default to not asking follow-up
        print(f"Warning: Could not analyze response quality: {str(e)}")
        output = {"should_ask_follow_up": False}

    # Record node execution end
    log_node_execution("analyze_response_quality_node", state, output)
    return output


def next_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for determining the next question to ask"""
    # Record node execution start
    log_node_execution("next_question_node", state, {})

    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)

    if not questions or current_index >= len(questions):
        output = {"interview_stage": "coding"}
        log_node_execution("next_question_node", state, output)
        return output

    # Move to next main question
    output = {
        "current_question_index": current_index + 1,
        "current_follow_up_index": -1,  # Reset to main question
        "interview_stage": "questioning",
    }
    log_node_execution("next_question_node", state, output)
    return output


def generate_coding_challenge_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating a coding challenge"""
    # Record node execution start
    log_node_execution("generate_coding_challenge_node", state, {})

    model = init_chat_model("deepseek-chat", temperature=0.5)

    prompt = """
    Generate a medium difficulty LeetCode-style coding challenge.
    It should be a well-known computer science problem that tests problem-solving skills.
    
    Format your response as JSON with this structure:
    {
      "title": "Problem title",
      "description": "Detailed problem description with examples",
      "difficulty": "medium",
      "solution": "Python solution code"
    }
    """

    try:
        response = model.invoke(
            [
                SystemMessage(
                    content="You are an expert in algorithms and data structures."
                ),
                HumanMessage(content=prompt),
            ]
        )

        # Record LLM call
        log_llm_call("deepseek-chat", prompt, response.content)

        parser = JsonOutputParser()
        challenge = parser.parse(response.content)
    except Exception as e:
        raise ValueError(f"Failed to generate coding challenge: {str(e)}")

    # Instead of asking the question directly, prepare it to be asked by another node
    # Store the challenge information in the state for the question asking node to use

    questions = state.get("interview_questions", [])
    questions.append(
        {
            "topic": "coding",
            "question": challenge.get("title", "")
            + "\n"
            + challenge.get("description", ""),
        }
    )

    output = {
        "interview_questions": questions,
    }

    # Record node execution end
    log_node_execution("generate_coding_challenge_node", state, output)
    return output


def evaluate_responses_node(state: InterviewState) -> Dict[str, Any]:
    """Node for evaluating candidate responses"""
    # Record node execution start
    log_node_execution("evaluate_responses_node", state, {})

    model = init_chat_model("deepseek-chat", temperature=0)

    # Prepare the data for evaluation
    evaluation_data = {
        "resume_content": state.get("resume_content", ""),
        "projects": state.get("projects", []),
        "technical_points": state.get("technical_points", []),
        "interview_questions": state.get("interview_questions", []),
    }

    prompt = f"""
    Based on the following interview data, evaluate the candidate and provide a score from 0-100 and feedback.
    
    Interview Data:
    {json.dumps(evaluation_data, indent=2)}
    
    Please provide:
    1. A score from 0-100 (where 60+ is passing, 80+ is good, 90+ is excellent)
    2. Detailed feedback explaining the score
    
    Format your response as JSON with this structure:
    {{
      "score": 85,
      "feedback": "Detailed feedback explaining the score"
    }}
    """

    try:
        response = model.invoke(
            [
                SystemMessage(
                    content="You are an expert technical interviewer and evaluator."
                ),
                HumanMessage(content=prompt),
            ]
        )

        # Record LLM call
        log_llm_call("deepseek-chat", prompt, response.content)

        parser = JsonOutputParser()
        evaluation = parser.parse(response.content)

        output = {
            "evaluation": evaluation,
            "final_score": evaluation.get("score"),
            "final_feedback": evaluation.get("feedback"),
            "interview_stage": "completed",
        }

        # Record node execution end
        log_node_execution("evaluate_responses_node", state, output)
        return output
    except Exception as e:
        raise ValueError(f"Failed to evaluate responses: {str(e)}")