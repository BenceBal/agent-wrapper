from langchain_core.messages import SystemMessage
from litellm import completion
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
import json

class VideoState(TypedDict):
    prompt: str
    storyboard: List[str]
    scenes: List[dict] # { "image_path": "...", "video_path": "..." }
    current_scene: int
    final_video: str

def director_node(state: VideoState):
    """
    The Director. Plans the video scene by scene.
    """
    print("--- [DIRECTOR] Creating Storyboard... ---")
    prompt = f"""
    You are a Film Director.
    Create a detailed storyboard for a video based on this prompt: '{state["prompt"]}'.
    Break it down into 3-5 scenes.
    
    Return JSON: {{ "scenes": ["Scene 1: Close up of...", "Scene 2: Wide shot of..."] }}
    """
    response = completion(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
    try:
        data = json.loads(response.choices[0].message.content)
        storyboard = data.get("scenes", [])
    except:
        storyboard = ["Generate video"]
    
    return {"storyboard": storyboard, "current_scene": 0, "scenes": []}

def artist_node(state: VideoState):
    """
    The Artist. Uses Flux/LoRA to generate the base image for the scene.
    """
    idx = state["current_scene"]
    scene_desc = state["storyboard"][idx]
    print(f"--- [ARTIST] Generating Image for: {scene_desc} ---")
    
    # Placeholder for Flux generation
    # image_path = flux_generate(scene_desc)
    image_path = f"scene_{idx}.png" 
    
    return {"scenes": state["scenes"] + [{"image_path": image_path}]}

def animator_node(state: VideoState):
    """
    The Animator. Uses LivePortrait/SVD to animate the image.
    """
    idx = state["current_scene"]
    # Placeholder for LivePortrait
    video_path = f"scene_{idx}.mp4"
    print(f"--- [ANIMATOR] Animating Scene {idx}... ---")
    
    return {"scenes": state["scenes"], "current_scene": idx + 1} # Update current scene

# Build Graph
workflow = StateGraph(VideoState)
workflow.add_node("director", director_node)
workflow.add_node("artist", artist_node)
workflow.add_node("animator", animator_node)

workflow.set_entry_point("director")
workflow.add_edge("director", "artist")
workflow.add_edge("artist", "animator")

def check_progress(state: VideoState):
    if state["current_scene"] >= len(state["storyboard"]):
        return END
    return "artist"

workflow.add_conditional_edges("animator", check_progress)
app = workflow.compile()
