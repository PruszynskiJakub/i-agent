def answer_prompt(dict  : dict) -> str:
    return f"""
   You are a helpful assistant. Here is the context you should use to answer the user's question:\n\n
   {dict['context']}\n\n
   Generate a clear and concise answer based solely on this context.
    """