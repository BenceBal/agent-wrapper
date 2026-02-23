from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from litellm import completion
import json
import os
from .tools import TOOLS

# --- 1. Define the State (Shared Memory) ---
class AgentState(TypedDict):
    task: str                 # The original user request
    plan: List[str]           # List of atomic steps to execute
    current_step_index: int   # Which step are we on?
    messages: List[BaseMessage] # Conversation history for the executor
    code_files: dict          # filename -> content (Metadata only, content on disk)
    review_feedback: str      # Feedback from reviewer (if rejected)
    final_output: str         # The result to show user

# --- 2. Define the Nodes (The Agents) ---

from .optimizer import DSPyOptimizer

# Initialize Optimizer
optimizer = DSPyOptimizer()

def planner_node(state: AgentState):
    """
    The Architect. Uses DSPy to generate optimized plans.
    """
    print("--- [PLANNER] Analyzing Request (DSPy)... ---")
    user_task = state["task"]
    
    try:
        # Use DSPy Logic
        steps_json = optimizer.optimize_plan(user_task)
        # Parse if string, or assume list if DSPy signature handled it
        if isinstance(steps_json, str):
            plan = json.loads(steps_json)
        else:
            plan = steps_json
    except:
        plan = ["Analyze task", "Execute task"] # Fallback

    print(f"--- [PLANNER] Generated Plan: {plan} ---")
    return {"plan": plan, "current_step_index": 0, "messages": [], "code_files": {}}

def executor_node(state: AgentState):
    """
    The Developer. Executes the current step using Claude 3 Opus and Tools.
    """
    current_idx = state["current_step_index"]
    plan = state["plan"]
    messages = state.get("messages", [])
    
    if current_idx >= len(plan):
        return {"final_output": "All steps completed."}

    current_task = plan[current_idx]
    print(f"--- [EXECUTOR] Working on: {current_task} ---")
    
    # Setup Claude with Tools
    # Note: Using 'claude-3-opus-20240229' or newer alias if available. 
    # For now defaulting to standard opus string which litellm handles.
    llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0) 
    llm_with_tools = llm.bind_tools(TOOLS)
    
    # Construct prompt context
    system_msg = SystemMessage(content=f"""
    You are an Expert Python Developer.
    Your goal is to complete the current task: {current_task}
    
    You have access to the file system. Use 'write_file' to create code, 'read_file' to check existing code.
    Always implement robust error handling.
    
    Feedback from Reviewer (if any): {state.get('review_feedback', 'None')}
    """)
    
    # If this is the first message for this step, add it
    if not messages:
        messages = [system_msg, HumanMessage(content=f"Execute step: {current_task}")]
    
    # Call Model
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    
    # Handle Tool Calls
    if response.tool_calls:
        print(f"--- [EXECUTOR] Calling Tools: {len(response.tool_calls)} ---")
        for tool_call in response.tool_calls:
            # Execute tool
            selected_tool = {t.name: t for t in TOOLS}[tool_call["name"]]
            tool_output = selected_tool.invoke(tool_call["args"])
            
            # Append result
            messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            print(f"    > Tool {tool_call['name']} output: {str(tool_output)[:50]}...")
            
        # Recursive call or loop back to model? 
        # For simplicity in this node, we return the state, and let the graph handle the loop back if needed.
        # But standard ReAct pattern requires calling model again after tool output.
        # We'll return messages and let a conditional edge decide if we need to call model again.
        return {"messages": messages}
    
    # If no tool calls, we assume task is done?
    # Or we check if the model said "I am done".
    return {"messages": messages, "review_feedback": ""} # Clear feedback, move to review

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
        # Clear messages for next step to save context
        return {"current_step_index": next_idx, "messages": []}
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

# Conditional Logic for Executor (Tool Loop)
def should_continue_tools(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the last message was a ToolMessage, we need to call the model again (Executor)
    if isinstance(last_message, ToolMessage):
        return "executor"
    
    # If the last message was an AIMessage with tool_calls, we need to process them? 
    # (In LangGraph, usually the node executes the tool calls and returns ToolMessages. 
    # My executor_node does both generation and execution which is anti-pattern for pure nodes, 
    # but fine for simple loops. Let's refine.)
    
    # Actually, if the last message has tool_calls, we executed them in the node 
    # and appended ToolMessages. So the last message IS ToolMessage (if we did it right).
    # Wait, looking at my executor logic:
    # 1. Invoke Model -> response (AIMessage)
    # 2. If tool_calls -> Execute -> Append ToolMessages
    # 3. Return.
    # So state["messages"][-1] is a ToolMessage.
    
    if isinstance(last_message, ToolMessage):
        return "executor" # Give model a chance to respond to tool output
        
    # If model replied with text (no tool calls), we go to reviewer
    return "reviewer"

workflow.add_conditional_edges("executor", should_continue_tools)

# Loop logic
def check_plan_progress(state: AgentState):
    if state["current_step_index"] >= len(state["plan"]):
        return END
    return "executor"

def review_logic(state: AgentState):
    if state.get("review_feedback"):
        return "executor" # Retry step
    return "check_progress" # Go to next step check

# workflow.add_edge("executor", "reviewer") # Removed direct edge, using conditional
workflow.add_conditional_edges("reviewer", check_plan_progress)

app = workflow.compile()
