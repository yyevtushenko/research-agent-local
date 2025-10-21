import importlib.util
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Maximum search query length to prevent sending entire prompts to search engines
MAX_SEARCH_QUERY_LENGTH = 1024


def truncate_query(query: str, max_length: int = MAX_SEARCH_QUERY_LENGTH) -> str:
    """
    Truncate search query to prevent sending entire prompts to search engines.

    Args:
        query: The search query to truncate
        max_length: Maximum allowed query length (default: 1024)

    Returns:
        Truncated query string
    """
    if len(query) > max_length:
        original_length = len(query)
        truncated = query[:max_length].strip()
        logger.warning(
            f"Search query truncated from {original_length} to {max_length} characters. "
            f"Original query was likely a full prompt instead of a concise search query. "
            f"Truncated query: '{truncated[:100]}...'"
        )
        return truncated
    return query


async def stream_output(log_type, step, content, websocket=None, with_data=False, data=None):
    """
    Stream output to the client.

    Args:
        log_type (str): The type of log
        step (str): The step being performed
        content (str): The content to stream
        websocket: The websocket to stream to
        with_data (bool): Whether to include data
        data: Additional data to include
    """
    if websocket:
        try:
            if with_data:
                await websocket.send_json({
                    "type": log_type,
                    "step": step,
                    "content": content,
                    "data": data
                })
            else:
                await websocket.send_json({
                    "type": log_type,
                    "step": step,
                    "content": content
                })
        except Exception as e:
            logger.error(f"Error streaming output: {e}")


def check_pkg(pkg: str) -> None:
    """
    Checks if a package is installed and raises an error if not.

    Args:
        pkg (str): The package name

    Raises:
        ImportError: If the package is not installed
    """
    if not importlib.util.find_spec(pkg):
        pkg_kebab = pkg.replace("_", "-")
        raise ImportError(
            f"Unable to import {pkg_kebab}. Please install with "
            f"`pip install -U {pkg_kebab}`"
        )


# Valid retrievers for fallback
VALID_RETRIEVERS = [
    "tavily",
    "custom",
    "duckduckgo",
    "searchapi",
    "serper",
    "serpapi",
    "google",
    "searx",
    "bing",
    "arxiv",
    "semantic_scholar",
    "pubmed_central",
    "exa",
    "mcp",
    "mock"
]


def get_all_retriever_names():
    """
    Get all available retriever names
    :return: List of all available retriever names
    :rtype: list
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Get all items in the current directory
        all_items = os.listdir(current_dir)

        # Filter out only the directories, excluding __pycache__
        retrievers = [
            item for item in all_items
            if os.path.isdir(os.path.join(current_dir, item)) and not item.startswith('__')
        ]

        return retrievers
    except Exception as e:
        logger.error(f"Error getting retrievers: {e}")
        return VALID_RETRIEVERS
