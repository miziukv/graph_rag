from openai import OpenAI
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

client = OpenAI()

def _count_tokens(text: str) -> int:
    """
    Count tokens using tiktoken for accurate measurement.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Number of tokens
    """
    encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    return len(encoding.encode(text))


def chunk(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter.
    Splits at natural boundaries (paragraphs, sentences, words) and measures by tokens.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum number of tokens per chunk (default: 500)
        chunk_overlap: Number of overlapping tokens between chunks (default: 50)
        
    Returns:
        List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=_count_tokens,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks


def embed(input: str) -> List[float]:
    """
    Generate embeddings using OpenAI's text-embedding-3-small model.
    
    Args:
        input: Text to embed
        
    Returns:
        Embedding vector as list of floats (1536 dimensions)
    """
    response = client.embeddings.create(
        input=input,
        model='text-embedding-3-small'
    )
    
    # Extract the actual vector from response
    return response.data[0].embedding