from pydantic_ai import Agent, PromptedOutput
from app.schemas.rag_response import RagResponse
from dotenv import load_dotenv
import os

load_dotenv()

# Default to a lightweight model if not specified
DEFAULT_MODEL = "ollama:qwen2.5:3b"

def get_rag_agent(model_name: str = DEFAULT_MODEL) -> Agent:
    """
    Factory function to create a PydanticAI Agent configured for RAG tasks.
    
    Args:
        model_name (str): The name of the model to use (e.g., 'ollama:qwen2.5:3b').
                          Must include the provider prefix if required by PydanticAI 
                          (though for Ollama local it's often just the model name or 'ollama:model').
    
    Returns:
        Agent: A configured PydanticAI Agent instance with the RagResponse result type.
    """
    
    # Define a system prompt that enforces the persona and constraints
    system_prompt = (
        "You are an expert technical assistant (PepoRAG). "
        "Your task is to answer questions based ONLY on the provided context. "
        "If the answer is not in the context, admit it. "
        "You must output your response strictly adhering to the RagResponse JSON schema. "
        "Analyze the context carefully before answering."
    )

    agent = Agent(
        model=model_name,
        output_type=PromptedOutput(RagResponse),
        system_prompt=system_prompt,
        retries=2  # Allow 2 retries for JSON validation failures
    )
    
    return agent
