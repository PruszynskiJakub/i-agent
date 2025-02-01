from tools.web import firecrawl_client
from tools.web.types import WebContent


async def scrape_webpage(url: str, format_type: str = 'md') -> WebContent:
    """
    Scrapes content from a URL and returns it as WebContent

    Args:
        url: The URL to scrape
        format_type: Format to return ('md' or 'html'), defaults to 'md'

    Returns:
        WebContent object with the scraped content

    Raises:
        ValueError: If URL is empty or format_type is invalid
    """
    if not url:
        raise ValueError("URL is required")

    if format_type not in ['md', 'html']:
        raise ValueError("Format must be 'md' or 'html'")

    try:
        formats = ['markdown'] if format_type == 'md' else ['html']
        data = firecrawl_client.scrape_url(url, params={'formats': formats})
        content = data.get('markdown' if format_type == 'md' else 'html', '')

        return WebContent(
            url=url,
            content=content,
            type=format_type
        )

    except Exception as e:
        raise RuntimeError(f"Failed to scrape URL: {str(e)}")
