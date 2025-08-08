"""
Centralized LLM configuration for the real estate AI application.
Provides consistent model selection across all agents and tools.
"""

def get_model_id(use_mini: bool = True, with_prefix: bool = True) -> str:
    """
    Get model ID with configurable variant and prefix options.
    
    Args:
        use_mini: If True, uses gpt-5-mini. If False, uses gpt-5 (default).
        with_prefix: If True, adds "openai:" prefix. If False, returns bare model name.
        
    Returns:
        str: Model ID, optionally with provider prefix
        
    Examples:
        get_model_id() -> "gpt-5"
        get_model_id(use_mini=True) -> "gpt-5-mini"
        get_model_id(with_prefix=True) -> "openai:gpt-5"
        get_model_id(use_mini=True, with_prefix=True) -> "openai:gpt-5-mini"
    """
    model = "gpt-5-mini" if use_mini else "gpt-5"
    return f"openai:{model}" if with_prefix else model


