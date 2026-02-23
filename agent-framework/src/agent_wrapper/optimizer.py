import dspy
from dspy.teleprompt import BootstrapFewShot

# Define the Signature
class PlannerSignature(dspy.Signature):
    """
    Break down a coding task into atomic implementation steps.
    """
    task_description = dspy.InputField(desc="The user's high-level request")
    steps = dspy.OutputField(desc="JSON list of execution steps")

class DSPyOptimizer:
    def __init__(self):
        # Configure DSPy with OpenAI/Claude
        # Note: Requires configuration in main setup
        self.lm = dspy.OpenAI(model='gpt-4o')
        dspy.settings.configure(lm=self.lm)
        
        self.planner = dspy.ChainOfThought(PlannerSignature)

    def optimize_plan(self, task: str):
        """
        Generate an optimized plan using Chain of Thought.
        """
        result = self.planner(task_description=task)
        return result.steps

    def train(self, examples):
        """
        Self-optimize using BootstrapFewShot.
        """
        teleprompter = BootstrapFewShot(metric=dspy.evaluate.answer_exact_match)
        self.planner = teleprompter.compile(self.planner, trainset=examples)
