from typing import List

def split_to_chunks(text: str, chunk_size: int = 3000) -> List[str]:
    """Split text into chunks of approximately chunk_size characters.
    
    Args:
        text: The text to split
        chunk_size: Target size for each chunk in characters
        
    Returns:
        List of text chunks, split on whitespace to avoid breaking words
    """
    chunks = []
    current_chunk = []
    current_size = 0
    
    # Split on whitespace to avoid breaking words
    words = text.split()
    
    for word in words:
        word_size = len(word) + 1  # Add 1 for the space
        
        if current_size + word_size > chunk_size and current_chunk:
            # Join current chunk and add to results
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
            
        current_chunk.append(word)
        current_size += word_size
        
    # Add the last chunk if there is one
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks
