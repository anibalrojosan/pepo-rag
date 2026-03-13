import logging

logger = logging.getLogger(__name__)

# Heuristic constants
COMPLEX_KEYWORDS = [
    "compare", "difference", "architect", "why", "how does", 
    "relationship", "explain in detail", "step by step",
    "pros and cons", "tradeoffs", "optimization", "bottleneck",
    "comparar", "diferencia", "arquitectura", "por qué", "cómo funciona",
    "relación", "explica en detalle", "paso a paso"
]

# Thresholds
LONG_QUERY_THRESHOLD = 150  # characters

# Model names (as expected by Ollama provider in PydanticAI)
FAST_MODEL = "ollama:granite3-dense:2b"
REASONING_MODEL = "ollama:qwen2.5:3b"

def get_model_for_query(query: str) -> str:
    """
    Analyzes the query complexity and returns the most suitable model.
    
    Args:
        query (str): The user's question.
        
    Returns:
        str: The Ollama model string to use.
    """
    query_lower = query.lower()
    
    # Rule 1: Length-based heuristic
    if len(query_lower) > LONG_QUERY_THRESHOLD:
        logger.info(f"Routing to {REASONING_MODEL} (Reason: Query length {len(query_lower)} > {LONG_QUERY_THRESHOLD})")
        return REASONING_MODEL
        
    # Rule 2: Keyword-based heuristic
    for keyword in COMPLEX_KEYWORDS:
        if keyword in query_lower:
            logger.info(f"Routing to {REASONING_MODEL} (Reason: Detected complex keyword '{keyword}')")
            return REASONING_MODEL
            
    # Default: Fast model
    logger.info(f"Routing to {FAST_MODEL} (Reason: Simple/Short query)")
    return FAST_MODEL
