from llmlingua import PromptCompressor
from onecontext import OneContext
import os

class MemoryManager:
    """
    Handles Long-Term Memory (OneContext) and Context Compression (LLMLingua).
    """
    def __init__(self, onecontext_api_key: str = None):
        self.compressor = PromptCompressor(model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank")
        self.oc = OneContext(api_key=onecontext_api_key or os.getenv("ONECONTEXT_API_KEY"))
        self.collection_name = "agent_wrapper_project"
        
        # Ensure collection exists
        if not self.oc.collection_exists(self.collection_name):
            self.oc.create_collection(self.collection_name)

    def store(self, key: str, value: str):
        """
        Store a document/snippet in OneContext.
        """
        self.oc.upsert(
            collection_name=self.collection_name,
            documents=[{"id": key, "content": value}],
            metadata=[{"type": "snippet"}]
        )

    def retrieve(self, query: str, top_k: int = 3):
        """
        Retrieve relevant context.
        """
        results = self.oc.query(
            collection_name=self.collection_name,
            query=query,
            top_k=top_k
        )
        return [res['content'] for res in results]

    def compress(self, context: str, instruction: str = "Keep only relevant code snippets.", target_token: int = 500):
        """
        Compress context using LLMLingua to fit within token limits.
        """
        compressed_prompt = self.compressor.compress_prompt(
            context,
            instruction=instruction,
            rate=0.5,
            condition_in_question="after_condition",
            reorder_context="sort"
        )
        return compressed_prompt['compressed_prompt']
