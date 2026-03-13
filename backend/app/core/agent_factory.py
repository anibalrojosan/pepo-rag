from pydantic_ai import Agent, PromptedOutput
from app.schemas.rag_response import RagResponse
from .model_router import get_model_for_query
from dotenv import load_dotenv

load_dotenv()

# Default to a lightweight model if not specified
DEFAULT_MODEL = "ollama:qwen2.5:3b"

def get_rag_agent(user_query: str = None, model_name: str = None) -> Agent:
    """
    Factory function to create a PydanticAI Agent configured for RAG tasks.
    
    Args:
        user_query (str, optional): The user's question to determine the model via routing.
        model_name (str, optional): Explicit model name to override routing.
    
    Returns:
        Agent: A configured PydanticAI Agent instance with the RagResponse result type.
    """
    
    # Determine the model dynamically if not explicitly provided
    if model_name is None:
        if user_query:
            model_name = get_model_for_query(user_query)
        else:
            model_name = DEFAULT_MODEL
    
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
