def answer_prompt(params: dict) -> str:
    return f"""
   You are a helpful assistant. Here is the context you should use to answer the user's question:\n\n
   {params['context']}\n\n
   Generate a clear and concise answer based solely on this context.
    """
