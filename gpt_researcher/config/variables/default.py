from .base import BaseConfig

DEFAULT_CONFIG: BaseConfig = {
    "RETRIEVER": "duckduckgo",
    "EMBEDDING": "openai:text-embedding-3-small",
    "SIMILARITY_THRESHOLD": 0.42,
    "FAST_LLM": "openai:gpt-4o-mini",
    # Has support for long responses (2k+ words).
    "SMART_LLM": "openai:gpt-4.1",
    # Can be used with o1 or o3, please note it will make tasks slower.
    "STRATEGIC_LLM": "openai:o4-mini",
    "FAST_TOKEN_LIMIT": 8000,  # Increased for longer responses
    "SMART_TOKEN_LIMIT": 16000,  # Increased for comprehensive reports (gpt-4o supports 16k output)
    "STRATEGIC_TOKEN_LIMIT": 8000,  # Increased for o1/o3 models
    "BROWSE_CHUNK_MAX_LENGTH": 8192,
    "CURATE_SOURCES": True,  # Enable by default to filter garbage content
    "SUMMARY_TOKEN_LIMIT": 700,
    "TEMPERATURE": 0.4,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "MAX_SEARCH_RESULTS_PER_QUERY": 20,  # Increased from 5 to 20 for better coverage
    # NO LIMIT - Qdrant handles millions of documents
    "MAX_CONTEXT_RESULTS_PER_QUERY": None,
    # Maximum search query length (hard limit to prevent sending entire prompts to search engines)
    "MAX_SEARCH_QUERY_LENGTH": 1024,
    "MEMORY_BACKEND": "local",
    "TOTAL_WORDS": 5000,  # Increased for comprehensive deep research reports (from 1200)
    "REPORT_FORMAT": "APA",
    "MAX_ITERATIONS": 3,
    "AGENT_ROLE": None,
    "SCRAPER": "bs",
    "MAX_SCRAPER_WORKERS": 15,
    "MAX_SUBTOPICS": 3,
    "LANGUAGE": "english",
    "REPORT_SOURCE": "web",
    "DOC_PATH": "./my-docs",
    "PROMPT_FAMILY": "default",
    "LLM_KWARGS": {},
    "EMBEDDING_KWARGS": {},
    "VERBOSE": False,
    # Deep research specific settings
    "DEEP_RESEARCH_BREADTH": 3,
    "DEEP_RESEARCH_DEPTH": 2,
    "DEEP_RESEARCH_CONCURRENCY": 4,

    # MCP retriever specific settings
    "MCP_SERVERS": [],  # List of predefined MCP server configurations
    # Whether to automatically select the best tool for a query
    "MCP_AUTO_TOOL_SELECTION": True,
    "MCP_ALLOWED_ROOT_PATHS": [],  # List of allowed root paths for local file access
    "MCP_STRATEGY": "fast",  # MCP execution strategy: "fast", "deep", "disabled"
    "REASONING_EFFORT": "medium",

    # Qdrant vector store settings
    "QDRANT_HOST": "localhost",
    "QDRANT_PORT": 6333,
    "QDRANT_API_KEY": None,
    "QDRANT_COLLECTION_NAME": "research_documents",
    # Default embedding model for Qdrant
    "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
    "QDRANT_ENABLED": True,  # Enable/disable Qdrant integration

    # LlamaCpp Embedding settings
    # Path to GGUF model file (e.g., Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf)
    "LLAMACPP_MODEL_PATH": None,

    # URL filtering - domains that provide low-quality or gibberish content
    "EXCLUDED_DOMAINS": [
        "support.microsoft.com",  # Technical support pages with gibberish
        "yandex.ru",
        "yandex.com",
        "accounts.google.com",
        "login.live.com",
        "help.netflix.com",
        "docs.microsoft.com",
        "answers.microsoft.com",
        "stackoverflow.com",
        "github.com",
        "search.brave.com"  # some yandex clone
    ],
}
