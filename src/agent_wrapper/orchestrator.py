from langchain_core.messages import HumanMessage, SystemMessage
from litellm import completion
from pydantic import BaseModel, Field
import os

class Orchestrator:
    """
    The Brain. Coordinates specialized agents.
    """
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.history = []

    def execute(self, user_task: str):
        """
        Main execution loop.
        """
        print(f"[*] Brain received: {user_task}")
        
        # 1. System Design Phase
        print("[*] Phase 1: Planning (System Design)...")
        plan = self._call_llm(
            system_prompt="You are a System Architect. Break down the user request into technical tasks. Be concise.",
            user_prompt=user_task
        )
        print(f"[*] Plan: {plan}")

        # 2. Tool Execution (Placeholder for Task Queue)
        # TODO: Implement LangGraph here for cyclical execution
        
        return "Plan generated (Execution logic pending)."

    def _call_llm(self, system_prompt: str, user_prompt: str):
        """
        Unified wrapper for LLM calls (OpenAI/Anthropic/Local).
        """
        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[!] LLM Error: {e}")
            raise e
