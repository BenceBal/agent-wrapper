from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from litellm import completion
import json

# --- 1. Define the State (Shared Memory) ---
class AgentState(TypedDict):
    task: str                 # The original user request
    plan: List[str]           # List of atomic steps to execute
    current_step_index: int   # Which step are we on?
    code_files: dict          # filename -> content
    review_feedback: str      # Feedback from reviewer (if rejected)
    final_output: str         # The result to show user

# --- 2. Define the Nodes (The Agents) ---

def planner_node(state: AgentState):
    """
    The Architect. Breaks the task into atomic steps.
    """
    print("--- [PLANNER] Analyzing Request... ---")
    user_task = state["task"]
    
    prompt = f"""
    You are a Senior Software Architect.
    Break down the following task into a list of atomic, sequential steps.
    Include steps for: Implementation, Logging, Error Handling, and Security Review.
    
    Task: {user_task}
    
    Return a JSON list of strings. Example: ["Create main.py", "Add logging config", "Implement auth logic"]
    """
    
    response = completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    # Parse JSON
    try:
        content = response.choices[0].message.content
        plan_data = json.loads(content)
        plan = plan_data.get("steps", plan_data if isinstance(plan_data, list) else [])
    except:
        plan = ["Analyze task", "Execute task"] # Fallback

    print(f"--- [PLANNER] Generated Plan: {plan} ---")
    return {"plan": plan, "current_step_index": 0, "code_files": {}}

def executor_node(state: AgentState):
    """
    The Developer. Executes the current step.
    """
    current_idx = state["current_step_index"]
    plan = state["plan"]
    
    if current_idx >= len(plan):
        return {"final_output": "All steps completed."}

    current_task = plan[current_idx]
    print(f"--- [EXECUTOR] Working on: {current_task} ---")
    
    # Context from previous steps
    context = f"Existing Files: {state['code_files'].keys()}"
    
    prompt = f"""
    You are an Expert Python Developer.
    Execute this specific task: {current_task}
    
    Context: {context}
    Feedback from Reviewer (if any): {state.get('review_feedback', 'None')}
    
    Return the code or action description.
    """
    
    response = completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    output = response.choices[0].message.content
    
    # Mocking file creation for now (In real version, this writes to disk)
    # state['code_files'][f"step_{current_idx}.py"] = output
    
    return {"review_feedback": ""} # Clear feedback

def reviewer_node(state: AgentState):
    """
    The Security Auditor. Reviews the work.
    """
    print("--- [REVIEWER] Inspecting Code... ---")
    
    # Logic: If step is 'Security Review', we are strict.
    # Random pass for MVP (Real version uses LLM to check code)
    is_approved = True 
    
    if is_approved:
        next_idx = state["current_step_index"] + 1
        return {"current_step_index": next_idx}
    else:
        return {"review_feedback": "Found a security vulnerability in input handling."}

# --- 3. Build the Graph ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("reviewer", reviewer_node)

# Set Entry Point
workflow.set_entry_point("planner")

# Define Edges
workflow.add_edge("planner", "executor")

# Conditional Logic: Loop until done
def should_continue(state: AgentState):
    if state["current_step_index"] >= len(state["plan"]):
        return END
    return "executor"

def review_logic(state: AgentState):
    if state.get("review_feedback"):
        return "executor" # Retry
    return "reviewer"

workflow.add_edge("executor", "reviewer")
workflow.add_conditional_edges("reviewer", should_continue)

app = workflow.compile()
