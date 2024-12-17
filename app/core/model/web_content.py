from dataclasses import dataclass


@dataclass
class WebContent:
    """Content fetched from a web URL"""
    url: str
    content: str
    type: str  # 'md' or 'html'