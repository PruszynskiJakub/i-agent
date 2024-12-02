def answer_prompt(dict  : dict) -> str:
    context = dict.get("context", "No context provided")
    query = dict.get("query", "No query provided")

    
    return f"""
   You are a helpful assistant. Here is the context you should use to answer the user's question:\n\n
   {context}\n\n
   Generate a clear and concise answer based solely on this context.
    """