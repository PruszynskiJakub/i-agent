import os

from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()
langfuse_client = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

