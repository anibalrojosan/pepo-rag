import logging
from typing import Any, Dict
from pydantic_ai import Agent
from .agent_factory import get_rag_agent
from .model_router import FAST_MODEL, REASONING_MODEL

logger = logging.getLogger(__name__)

async def run_agent_with_fallback(user_query: str, context: str) -> Any:
    """
    Executes the RAG agent with a fallback mechanism.
    If the first model fails (e.g., validation error), it retries with the alternate model.
    
    Args:
        user_query (str): The user's question.
        context (str): The retrieved context from technical books.
        
    Returns:
        Any: The validated RagResponse object.
    """
    
    # Get agent (routing happens inside factory)
    agent = get_rag_agent(user_query=user_query)
    primary_model = agent.model_name
    
    try:
        logger.info(f"Executing primary model: {primary_model}")
        result = await agent.run(user_query, deps=context)
        return result.data
        
    except Exception as e:
        logger.warning(f"Primary model {primary_model} failed: {e}. Attempting fallback...")
        
        # Determine fallback model
        fallback_model = REASONING_MODEL if primary_model == FAST_MODEL else FAST_MODEL
        
        try:
            logger.info(f"Executing fallback model: {fallback_model}")
            fallback_agent = get_rag_agent(model_name=fallback_model)
            result = await fallback_agent.run(user_query, deps=context)
            return result.data
        except Exception as fallback_error:
            logger.error(f"Fallback model {fallback_model} also failed: {fallback_error}")
            raise fallback_error
