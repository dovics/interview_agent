"""
Node functions for the Interview Agent.

This module contains all the node functions used in the interview agent workflow.
"""

import json
from typing import Dict, Any
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

from .parser import parse_resume
from .logger import log_node_execution, log_llm_call
from .types import InterviewState


def upload_resume_node(state: InterviewState) -> Dict[str, Any]:
    """Node for uploading and parsing resume"""
    # 记录节点执行开始
    log_node_execution("upload_resume_node", state, {})
    
    # Get file path from state
    file_path = state.get("messages", [{}])[0].get("file_path") if state.get("messages") else None
    
    # If no file path provided, raise an error
    if not file_path:
        raise ValueError("No resume file path provided. Please provide a path to a PDF, DOCX, or Markdown file.")
    
    try:
        # Parse the actual file
        resume_content = parse_resume(file_path)
        
        # Check if resume content is empty
        if not resume_content or not resume_content.strip():
            raise ValueError(f"Parsed resume content is empty for file: {file_path}")
            
    except Exception as e:
        # If parsing fails, raise an error with details
        raise ValueError(f"Failed to parse resume file '{file_path}': {str(e)}")
    
    result = {
        "resume_content": resume_content,
        "interview_stage": "resume_analysis"
    }
    
    # 记录节点执行结束
    log_node_execution("upload_resume_node", state, result)
    return result


def analyze_resume_node(state: InterviewState) -> Dict[str, Any]:
    """Node for analyzing resume and extracting projects and technical points"""
    # 记录节点执行开始
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
        response = model.invoke([
            SystemMessage(content="You are an expert technical recruiter."),
            HumanMessage(content=prompt)
        ])
        
        # 记录LLM调用
        log_llm_call("deepseek-chat", prompt, response.content)
        
        # Parse the JSON response
        parser = JsonOutputParser()
        result = parser.parse(response.content)
        
        projects = result.get("projects", [])
        technical_points = result.get("technical_points", [])
        
        output = {
            "projects": projects,
            "technical_points": technical_points,
            "interview_stage": "questioning"
        }
        
        # 记录节点执行结束
        log_node_execution("analyze_resume_node", state, output)
        return output
    except Exception as e:
        raise ValueError(f"Failed to analyze resume: {str(e)}")


def generate_questions_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating interview questions"""
    # 记录节点执行开始
    log_node_execution("generate_questions_node", state, {})
    
    model = init_chat_model("deepseek-chat", temperature=0.7)
    
    # Combine projects and technical points for question generation
    topics = []
    
    for project in state.get("projects", []):
        topics.append({
            "type": "project",
            "title": project["title"],
            "description": project["description"],
            "technologies": project["technologies"]
        })
    
    for tech_point in state.get("technical_points", []):
        topics.append({
            "type": "technical",
            "name": tech_point["name"],
            "description": tech_point["description"]
        })
    
    # Generate questions for each topic
    all_questions = []
    
    for topic in topics:
        if topic["type"] == "project":
            prompt = f"""
            Based on this project:
            Title: {topic['title']}
            Description: {topic['description']}
            Technologies: {', '.join(topic['technologies'])}
            
            Generate a main interview question and 2 follow-up questions about this project.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['title']}",
              "question": "Main question about the project",
              "follow_up_questions": [
                "Follow-up question 1",
                "Follow-up question 2"
              ]
            }}
            """
        else:  # technical point
            prompt = f"""
            Based on this technical skill:
            Name: {topic['name']}
            Description: {topic['description']}
            
            Generate a main interview question and 2 follow-up questions about this technical skill.
            
            Format your response as JSON with this structure:
            {{
              "topic": "{topic['name']}",
              "question": "Main question about the technical skill",
              "follow_up_questions": [
                "Follow-up question 1",
                "Follow-up question 2"
              ]
            }}
            """
        
        try:
            response = model.invoke([
                SystemMessage(content="You are an expert technical interviewer."),
                HumanMessage(content=prompt)
            ])
            
            # 记录LLM调用
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
        "interview_stage": "questioning"
    }
    
    # 记录节点执行结束
    log_node_execution("generate_questions_node", state, output)
    return output


def ask_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for presenting questions to the candidate and collecting answers"""
    # 记录节点执行开始
    log_node_execution("ask_question_node", state, {})
    
    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    
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
            "interview_stage": "questioning"
        }
        log_node_execution("ask_question_node", state, output)
        return output
    
    # Display the question to the candidate
    print(f"\nQuestion: {question_text}")
    print("-" * 50)
    
    # Get answer from terminal input
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
        "interview_stage": "questioning"
    }
    
    # 记录节点执行结束
    log_node_execution("ask_question_node", state, output)
    return output


def generate_adaptive_questions_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating adaptive follow-up questions based on candidate's answers"""
    # 记录节点执行开始
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
        response = model.invoke([
            SystemMessage(content="You are an expert technical interviewer skilled at asking deep follow-up questions."),
            HumanMessage(content=prompt)
        ])
        
        # 记录LLM调用
        log_llm_call("deepseek-chat", prompt, response.content)
        
        parser = JsonOutputParser()
        result = parser.parse(response.content)
        adaptive_question = result.get("adaptive_question", "")
        
        # Display the adaptive question to the candidate
        if adaptive_question:
            print(f"\nFollow-up: {adaptive_question}")
            print("-" * 50)
            
            # Get answer to the adaptive question
            adaptive_answer = input("Your answer: ").strip()
            
            # Update the interview questions with the adaptive question and answer
            updated_questions = list(questions)
            current_q_set_copy = dict(updated_questions[current_index])
            
            # Add adaptive question and answer to the set
            if "adaptive_questions" not in current_q_set_copy:
                current_q_set_copy["adaptive_questions"] = []
            
            current_q_set_copy["adaptive_questions"].append({
                "question": adaptive_question,
                "answer": adaptive_answer
            })
            
            updated_questions[current_index] = current_q_set_copy
            
            output = {
                "interview_questions": updated_questions
            }
            
            # 记录节点执行结束
            log_node_execution("generate_adaptive_questions_node", state, output)
            return output
    except Exception as e:
        # If we can't generate an adaptive question, continue with regular flow
        print(f"Warning: Could not generate adaptive question: {str(e)}")
    
    output = {}
    log_node_execution("generate_adaptive_questions_node", state, output)
    return output


def next_question_node(state: InterviewState) -> Dict[str, Any]:
    """Node for determining the next question to ask"""
    # 记录节点执行开始
    log_node_execution("next_question_node", state, {})
    
    questions = state.get("interview_questions", [])
    current_index = state.get("current_question_index", 0)
    follow_up_index = state.get("current_follow_up_index", -1)
    
    if not questions or current_index >= len(questions):
        output = {"interview_stage": "coding"}
        log_node_execution("next_question_node", state, output)
        return output
    
    current_q_set = questions[current_index]
    follow_ups = current_q_set.get("follow_up_questions", [])
    
    # If we're on the main question (-1) or haven't finished follow-ups, continue with follow-ups
    if follow_up_index < len(follow_ups) - 1:
        # Move to next follow-up question
        output = {
            "current_follow_up_index": follow_up_index + 1,
            "interview_stage": "questioning"
        }
        log_node_execution("next_question_node", state, output)
        return output
    # If we've finished follow-ups and there are more question sets, go to next set
    elif current_index < len(questions) - 1:
        # Move to next main question
        output = {
            "current_question_index": current_index + 1,
            "current_follow_up_index": -1,  # Reset to main question
            "interview_stage": "questioning"
        }
        log_node_execution("next_question_node", state, output)
        return output
    # Otherwise, move to coding challenge
    else:
        output = {"interview_stage": "coding"}
        log_node_execution("next_question_node", state, output)
        return output


def generate_coding_challenge_node(state: InterviewState) -> Dict[str, Any]:
    """Node for generating a coding challenge"""
    # 记录节点执行开始
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
        response = model.invoke([
            SystemMessage(content="You are an expert in algorithms and data structures."),
            HumanMessage(content=prompt)
        ])
        
        # 记录LLM调用
        log_llm_call("deepseek-chat", prompt, response.content)
        
        parser = JsonOutputParser()
        challenge = parser.parse(response.content)
        
        # Ask for solution from candidate
        print(f"\nCoding Challenge: {challenge.get('title', '')}")
        print("=" * 50)
        print(f"{challenge.get('description', '')}")
        print("-" * 50)
        solution = input("Write your solution:\n").strip()
        
        output = {
            "coding_challenge": challenge,
            "coding_solution": solution,
            "interview_stage": "evaluation"
        }
        
        # 记录节点执行结束
        log_node_execution("generate_coding_challenge_node", state, output)
        return output
    except Exception as e:
        raise ValueError(f"Failed to generate coding challenge: {str(e)}")


def evaluate_responses_node(state: InterviewState) -> Dict[str, Any]:
    """Node for evaluating candidate responses"""
    # 记录节点执行开始
    log_node_execution("evaluate_responses_node", state, {})
    
    model = init_chat_model("deepseek-chat", temperature=0)
    
    # Prepare the data for evaluation
    evaluation_data = {
        "resume_content": state.get("resume_content", ""),
        "projects": state.get("projects", []),
        "technical_points": state.get("technical_points", []),
        "interview_questions": state.get("interview_questions", []),
        "coding_challenge": state.get("coding_challenge", {}),
        "coding_solution": state.get("coding_solution", "")
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
        response = model.invoke([
            SystemMessage(content="You are an expert technical interviewer and evaluator."),
            HumanMessage(content=prompt)
        ])
        
        # 记录LLM调用
        log_llm_call("deepseek-chat", prompt, response.content)
        
        parser = JsonOutputParser()
        evaluation = parser.parse(response.content)
        
        output = {
            "evaluation": evaluation,
            "final_score": evaluation.get("score"),
            "final_feedback": evaluation.get("feedback"),
            "interview_stage": "completed"
        }
        
        # 记录节点执行结束
        log_node_execution("evaluate_responses_node", state, output)
        return output
    except Exception as e:
        raise ValueError(f"Failed to evaluate responses: {str(e)}")