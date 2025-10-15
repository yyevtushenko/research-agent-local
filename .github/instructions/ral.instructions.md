---
applyTo: '**'
---

# Research Agent Local - Copilot Instructions

## Project Overview

Research Agent Local is an **Autonomous Research System** built with Python that integrates multiple AI models and web search APIs to conduct comprehensive online research and generate detailed reports. The system processes web content, documents, and structured data sources using LLM-powered analysis to produce high-quality research outputs across various formats.

### Error Handling

- Always raise proper `Exception` subclasses (not strings)  
- Handle errors meaningfully (don't just log and ignore)  
- Use `Optional` and `Union` types for error handling when appropriate  
- Implement error boundaries and fallback mechanisms

Research Agent Local is a unified system that supports multiple deployment configurations:
- **FastAPI Backend**: RESTful API server for programmatic access
- **Multi-Agent System**: Coordinated research team with specialized roles
- **Frontend Options**: HTML/JavaScript and Next.js interfaces  
- **CLI Tools**: Command-line interface for batch processing

The system operates as a single cohesive application with modular components for different research workflows.

## External Integrations

### Web Search APIs
- **Tavily Search**: Primary web search API via `gpt_researcher.retrievers.tavily`
- **Google Search**: Google Custom Search integration via `gpt_researcher.retrievers.google`
- **Bing Search**: Microsoft Bing API via `gpt_researcher.retrievers.bing`
- **DuckDuckGo**: Free search via `gpt_researcher.retrievers.duckduckgo`
- **Multiple Providers**: Support for SearchAPI, SerpAPI, Serper, and custom search engines

### AI/LLM Services  
- **OpenAI GPT**: Primary models (GPT-4o, GPT-4o-mini, o4-mini) via `langchain_openai`
- **Claude**: Anthropic models via `langchain_anthropic`
- **Gemini**: Google models via `langchain_google_genai`
- **AI/ML API**: 300+ models provider with enterprise-grade limits
- **Local LLM**: Support for various local model providers
- **Token Tracking**: Cost monitoring and usage tracking across all providers

### Document Processing & Storage
- **Web Scraping**: Multiple scrapers (BeautifulSoup, Firecrawl, Tavily Extract) in `gpt_researcher.scraper`
- **Document Loading**: Support for PDFs, DOCX, TXT via `gpt_researcher.document`
- **Vector Storage**: Qdrant integration for semantic search and context retrieval
- **Memory Backend**: Local and cloud-based conversation memory systems

### Model Context Protocol (MCP)
- **MCP Integrations**: Standardized tool access via `gpt_researcher.mcp`
- **GitHub MCP**: Repository analysis and code research
- **Filesystem MCP**: Local file system access with security boundaries
- **Custom MCP Servers**: Support for external tool integrations

### Research Processing Pipeline
1. **Query Planning** → LLM analysis → Research sub-queries
2. **Information Gathering** → Multi-source search → Content extraction
3. **Context Processing** → Vector storage → Semantic analysis
4. **Report Generation** → LLM synthesis → Formatted output
5. **Multi-Agent Coordination** → Specialized roles → Quality assurance

## Architecture Components

### Multi-Deployment Setup
- **FastAPI Backend** (`backend/server/app.py`): RESTful API server with WebSocket support
- **Multi-Agent System** (`multi_agents/`): Coordinated research team with specialized agents
- **Frontend Options**: HTML/JavaScript (`frontend/`) and Next.js (`frontend/nextjs/`) interfaces
- **CLI Tools** (`cli.py`, `main.py`): Command-line interface for direct Python usage

### Web Interface & API
- **Tech Stack:** FastAPI, WebSocket, CORS-enabled
- **Features:**
  - RESTful API endpoints for research tasks
  - Real-time WebSocket communication for progress updates
  - File upload/download capabilities (PDF, DOCX, MD)
  - Chat interface with memory and context
  - Multi-format report generation
  - Background task processing

### Core Research Engine
- **Location:** `gpt_researcher/`
- **Tech Stack:** Python, LangChain, Pydantic, LangGraph
- **Features:**
  - Multi-source web search and content retrieval
  - LLM orchestration and agent coordination
  - Document processing and vector storage
  - MCP integration for external tool access
  - Advanced research strategies (deep research, hybrid research)
  - Cost tracking and performance monitoring

### Multi-Agent System
- **Location:** `multi_agents/`
- **Agent Types:**
  - `ResearchAgent`: Conducts initial and depth research
  - `WriterAgent`: Generates report content and sections
  - `EditorAgent`: Manages research workflow and coordination
  - `ReviewerAgent`: Quality assurance and validation
  - `ReviserAgent`: Content refinement and improvement
  - `PublisherAgent`: Final report formatting and output
  - `ChiefEditorAgent`: Orchestrates the entire research team

### Key Service Layer
All business logic lives in `gpt_researcher/`:
- `agent.py`: Core GPTResearcher class and research orchestration
- `skills/`: Specialized research skills (researcher, writer, context manager, etc.)
- `actions/`: Core research actions (retrieval, scraping, report generation)
- `retrievers/`: Multiple search provider integrations
- `scraper/`: Web content extraction and processing
- `llm_provider/`: LLM integration and provider management

### Data Processing Stack
- **Web Search**: Multi-provider search and content retrieval
- **LangChain**: AI model orchestration and chaining
- **LangGraph**: Multi-agent workflow coordination
- **Pydantic**: Data validation and type safety
- **Vector Storage**: Qdrant for semantic search and context storage
- **FastAPI**: RESTful API and WebSocket communication

#### Configuration System
- **Location:** `gpt_researcher/config/`
- **Purpose:** Environment configuration, API keys, model settings
- **Features:**
  - API token management (OpenAI, Tavily, Google, etc.)
  - Model configuration and parameter settings
  - Search provider configuration
  - Environment-based configuration loading
  - JSON-based custom configurations

#### Core Library Architecture
- **Location:** `gpt_researcher/`
- **Purpose:** Reusable research components and skills
- **Features:**
  - Modular skill-based architecture
  - Multiple retriever and scraper integrations
  - LLM provider abstraction layer
  - Vector storage and memory management
  - MCP integration for external tools
  - Report generation and formatting

#### Architecture Diagram
```
[Frontend UI] <-> [FastAPI Backend] <-> [GPT Researcher] <-> [Multi-Agents] <-> [LLM Models]
     |               |                      |                    |              |
 User Interface  WebSocket API     Research Engine      Agent Coordination  GPT/Claude/Gemini
     |               |                      |                    |              |
[CLI Interface] <-> [Config System] <-> [Web Retrievers] <-> [MCP Tools] <-> [Vector Store]
```

---

## **Technical Requirements**

- Ensure thread-safe operations for concurrent access  
- Implement proper error handling and fallback mechanisms  
- Design for scalability to handle large conversation histories  
- Include monitoring and logging for system performance tracking  
- All logs must use Python's standard **`logging`** module (❌ no `print()` for debugging)  
- Use **pip** with virtual environments (❌ no global installs). Project venv is ~/work/ : `$ source ~/work/bin/activate`, apply it before running any scripts
- **NO NEW FILES** without explicit approval (no new APIs, test scripts, docs, or summaries)  
- **NO NEW PROMPTS** without explicit approval (human should ask for new prompts explicitly)  
- Extend existing modules instead of creating new ones  
- Keep presentation logic and business logic separate  
- **Security First**: validate input, sanitize output, and follow security best practices  
- **Performance Monitoring**: include metrics in all critical paths  
- Before implementing new code, always check:
  - Can existing code be extended instead?  
  - Is there a maintained library available?  
  - Is there a native API available?  
  - Are you using modern, actively maintained packages?  
- ❌ **Never use dynamic imports** (`import XXX from YYY` in the middle of a function).  This code is penalized and ***immediately rolled back***

---

## **Python Development Guidelines**

- Always use **type hints** for function parameters and return types
- Prefer **dataclasses** or **Pydantic models** over plain dictionaries for structured data
- Use **pathlib.Path** instead of string manipulation for file paths
- Use **f-strings** for string formatting (not `.format()` or `%` formatting)
- Mark immutable data with **frozen dataclasses** or **Final** type hints
- Use **enum.Enum** for constants with multiple related values
- Add **docstrings** for all public functions and classes
- Avoid bare `except:` → prefer specific exception types
- Use **context managers** (`with` statements) for resource management
- Use **list comprehensions** and **generator expressions** where appropriate
- Follow **PEP 8** style guidelines strictly
- Remove dead code (unused imports, functions, commented-out code)  

---

## Development Workflows

### Starting Development
```bash
# Create virtual environment (first time setup)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend (recommended for development)
uvicorn backend.server.app:app --reload --host 0.0.0.0 --port 8000

# Or start with main.py
python main.py

# Or run CLI directly
python cli.py "Your research query"

# Or run multi-agents system
python multi_agents/main.py
```

### Key Scripts
```bash
python main.py                  # Start FastAPI server
python cli.py "query"          # Direct CLI research
python multi_agents/main.py    # Multi-agent research system
python backend/run_server.py   # Alternative server startup
uvicorn backend.server.app:app --reload  # Development server with hot reload
```

## Critical Patterns

### Service Architecture
- **NO business logic in UI components** - use services from `gpt_researcher/`
- **Factory Pattern**: `llm_provider/` manages LLM model creation
- **Wrapper Pattern**: Search APIs wrapped in `gpt_researcher.retrievers/` modules

### Logging Convention
```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging with appropriate levels
logger.info('Research operation', extra={'query': query, 'report_type': report_type})
logger.error('API call failed', extra={'api': 'tavily', 'error': str(e)})
# Never use print() - always use the logging module
```

### Validation Strategy
- **Pydantic models**: All API wrappers use Pydantic for validation
- **Runtime validation**: Services validate inputs/outputs with Pydantic
- **LLM response validation**: Always validate AI responses before processing

### Multi-Agent Architecture
```python
# Each agent has specialized role in research workflow
# gpt_researcher/ contains core research functionality
# Multi-agent system coordinates specialized research tasks
```

### Configuration Management
- **Location:** `gpt_researcher/config/` and environment variables
- **Purpose:** Environment configuration, API keys, model settings
- **Features:**
  - API token management (OpenAI, Tavily, Google, etc.)
  - Model configuration and parameter settings
  - Search provider configuration
  - Environment-based configuration loading

### Key System Features
- Autonomous research with multiple data sources
- LLM-powered content analysis and report generation
- Modular, extensible Python architecture
- Pydantic-based validation and API integration
- Cost tracking and token usage monitoring
- Multi-format report generation (PDF, DOCX, Markdown)
- Multi-agent coordination and quality assurance

---

## **Clean Code Principles**

### Naming Conventions

- Use descriptive, pronounceable, and searchable names  
- Avoid redundant context (❌ `car.carColor`, ✅ `car.color`)  
- Use meaningful distinctions and avoid mental mapping  
- Don’t use prefixes or encodings in variable names  
- **Keep function names short when the context makes meaning obvious**  
  - ✅ Inside `user_service.py`: `create`, `update`, `delete`  
  - ❌ `create_user`, `update_user`, `delete_user` (redundant)  
  - ✅ Inside `auth_controller.py`: `login`, `logout`  
  - ❌ `auth_login`, `auth_logout`  

### Function Design

- Functions should follow **single responsibility**: each function does one thing.
- **Descriptive names**: names should clearly indicate what the function does (e.g. getUserProfile, not getData).
- Try to keep functions short (≈ ≤ 20 lines). If a function grows beyond that, consider splitting it.
- Limit parameters: **ideally 3-4 parameters; never more than 5** unless absolutely justified. Use object parameter destructuring when many optional parameters are needed.
- Prefer **pure / stateless functions** wherever possible (no side-effects, same input → same output).

### Code Splitting & File Organization

- **One class per file**.
- **One API endpoint per file**.
- **One main function per file**.
- **Exception**: Utility functions with a shared domain (e.g., db_utils.py, string_utils.py).
- Group **Pydantic models, getters, and setters** logically in the same file if they operate on the same entity.
- Keep files **cohesive**: everything inside should belong to the same logical unit.
- Avoid files with only one-liner functions unless absolutely necessary.
- Don't create very large files (>300 lines) - split them logically. 
- Functions should fit within a single screen (≈ 20-30 lines).
- Too long if or else blocks? Consider extracting to separate functions. The same with while loops and try/catch blocks.

✅ Good
user_model.py

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    name: str
    email: str
    age: int

def get_user_by_id(user_id: str) -> Optional[User]:
    return db.get_user(user_id)

def save_user(user: User) -> User:
    return db.save_user(user)
```

❌ Bad

Mixing unrelated models and helpers (User + Product + DateUtils in one file).

Putting one-liner functions in separate files just to follow "one function per file".

---

### Error Handling

- Always throw `Error` objects (not strings)  
- Handle errors meaningfully (don’t just log and ignore)  
- Use `Result<T, E>` when appropriate  
- Implement error boundaries and fallback mechanisms  

#### Error Handling Example

✅ Good

```python
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

def fetch_user_data(user_id: str) -> Optional[dict]:
    """Fetch user data with proper error handling."""
    try:
        # Simulate API call
        user_data = api_client.get_user(user_id)
        if not user_data:
            logger.warning(f"User not found: {user_id}")
            return None
        return user_data
    except ConnectionError as e:
        logger.error(f"Connection failed for user {user_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching user {user_id}: {e}")
        return None
```

❌ Bad

```python
def fetch_user_data(user_id: str):
    return api_client.get_user(user_id)  # throws raw API errors
```

---

## FastAPI & Frontend UI Best Practices

### Modern FastAPI Guidelines

- Keep **UI logic separate** from business logic
- Use **WebSocket** for real-time communication
- Keep API endpoints **small and focused**
- Separate **data processing** from **presentation logic**
- Use proper **async/await** patterns for I/O operations
- Implement proper request validation with Pydantic models

### Modern Frontend Patterns

- **State Management**:
  - Use proper state management in frontend frameworks
  - Handle WebSocket connections properly for real-time updates
  - Implement proper error boundaries and fallback mechanisms
  - Cache expensive operations where appropriate

- **API Integration**:
  - Use proper HTTP clients for API communication
  - Handle authentication and authorization properly
  - Implement proper retry logic for failed requests
  - Use proper loading states and error handling

- **Performance Optimization**:
  - Minimize API calls with proper caching strategies
  - Use WebSocket for real-time updates instead of polling
  - Implement proper loading states with progress indicators
  - Use proper error boundaries and fallback mechanisms

✅ Modern FastAPI (2024)

```python
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from pydantic import BaseModel
from gpt_researcher import GPTResearcher
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResearchRequest(BaseModel):
    query: str
    report_type: str = "research_report"
    report_source: str = "web"
    
@app.post("/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start research task with proper validation and error handling."""
    try:
        # Validate request
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Create researcher instance
        researcher = GPTResearcher(
            query=request.query,
            report_type=request.report_type,
            report_source=request.report_source
        )
        
        # Start background task
        background_tasks.add_task(conduct_research_task, researcher)
        
        return {"status": "started", "message": "Research task initiated"}
        
    except Exception as e:
        logger.error(f"Research initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Research task failed to start")

async def conduct_research_task(researcher: GPTResearcher):
    """Background task for conducting research."""
    try:
        context = await researcher.conduct_research()
        report = await researcher.write_report()
        logger.info(f"Research completed for query: {researcher.query}")
        
    except Exception as e:
        logger.error(f"Research task failed: {e}")
```

❌ Bad Patterns

```python
# Don't mix business logic with API endpoints
@app.post("/research")
async def bad_research(query: str):
    # Direct LLM calls in endpoint - move to service layer
    response = llm.invoke(query)
    return response

# Don't ignore error handling
@app.post("/research")
async def bad_research_no_errors(query: str):
    researcher = GPTResearcher(query=query)
    return await researcher.write_report()  # No error handling
```

### LangChain Integration Best Practices

- **Agent and Tool Integration**:
  - Use `create_tool_calling_agent()` for modern agent creation
  - Implement proper tool validation with Pydantic models
  - Use `AgentExecutor` for reliable agent execution with error handling
  - Cache LLM clients as resources, not data

✅ Modern LangChain Integration

```python
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

@tool
def search_web_content(query: str, max_results: int = 5) -> str:
    """Search for web content based on query."""
    # Implementation with proper validation
    from gpt_researcher.retrievers.tavily import TavilySearch
    search = TavilySearch(query)
    results = search.search(max_results=max_results)
    return f"Found {len(results)} results for '{query}'"

def get_llm_client(model_name: str):
    """Get cached LLM client."""
    return ChatOpenAI(model=model_name, temperature=0)

def create_research_agent(model_name: str = "gpt-4o-mini"):
    """Create and configure a research agent."""
    llm = get_llm_client(model_name)
    tools = [search_web_content]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research assistant. Use the available tools to gather information and provide comprehensive answers."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

# Usage in FastAPI
async def run_research_query(query: str, model: str):
    """Run research query with proper error handling."""
    try:
        agent_executor = create_research_agent(model)
        result = await agent_executor.ainvoke({"input": query})
        return result.get("output", "No response")
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return None
```

### Data Processing Best Practices

- **Separation of Concerns**:
  - Business logic in `gpt_researcher/` modules only
  - UI logic in frontend only (presentation layer)
  - Configuration in `gpt_researcher/config/`
  - Agent and tool definitions in dedicated modules

- **Modern Error Handling**:
  - Use proper HTTP status codes and error responses
  - Log detailed errors for debugging with proper logging
  - Provide fallback options when possible
  - Implement proper retry mechanisms for external API calls

- **API Design**:
  - Use proper REST conventions for API endpoints
  - Implement proper request/response models with Pydantic
  - Handle authentication and authorization properly
  - Use WebSocket for real-time communication

---

## **Industry Standard Guidelines**

- Follow **PEP 8** Python Style Guide and Google Python standards
- Max line length: 88 characters (Black formatter standard)
- Use **docstrings** for public APIs (Google or NumPy style)
- Follow SOLID principles:
  - **S**ingle Responsibility  
  - **O**pen/Closed  
  - **L**iskov Substitution  
  - **I**nterface Segregation  
  - **D**ependency Inversion  
- Use **PascalCase** for classes and exceptions
- Use **snake_case** for variables, functions, and methods
- Use **SCREAMING_SNAKE_CASE** for constants
- Use **snake_case** for file names
- Prefer explicit type hints for public functions

---

## **Object-Oriented Programming Principles**

- **Encapsulation** → use private methods with leading underscore
- **Abstraction** → hide implementation behind clean interfaces
- **Inheritance** → use abstract base classes wisely
- **Polymorphism** → leverage duck typing and protocols
- Use **dependency injection** for testability

---

## **Performance & Optimization (Latest Patterns)**

- Use **proper caching** strategies with TTL-based invalidation
- Implement proper **memoization** for expensive computations
- Use **asyncio** for concurrent operations and I/O-bound tasks
- Optimize imports (avoid importing heavy libraries unnecessarily)
- Implement proper **connection pooling** for APIs
- Use **background tasks** for long-running operations
- Implement proper loading states and progress indicators
- Cache LLM clients and expensive resources at application level

### Modern Caching Patterns

```python
import functools
import asyncio
from typing import Any, Dict, Optional
from gpt_researcher import GPTResearcher
from datetime import datetime, timedelta

# Application-level caching for LLM clients
_llm_client_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, datetime] = {}
_cache_ttl = timedelta(hours=1)

def get_cached_llm_client(model_name: str, temperature: float = 0.0):
    """Cache LLM client at application level."""
    cache_key = f"{model_name}_{temperature}"
    
    # Check if cache is still valid
    if cache_key in _cache_timestamps:
        if datetime.now() - _cache_timestamps[cache_key] > _cache_ttl:
            # Cache expired, remove it
            _llm_client_cache.pop(cache_key, None)
            _cache_timestamps.pop(cache_key, None)
    
    if cache_key not in _llm_client_cache:
        from langchain_openai import ChatOpenAI
        _llm_client_cache[cache_key] = ChatOpenAI(model=model_name, temperature=temperature)
        _cache_timestamps[cache_key] = datetime.now()
    
    return _llm_client_cache[cache_key]

# Function-level caching with TTL
@functools.lru_cache(maxsize=128)
def get_search_results_cached(query: str, max_results: int = 5) -> str:
    """Cache search results with LRU eviction."""
    from gpt_researcher.retrievers.tavily import TavilySearch
    search = TavilySearch(query)
    results = search.search(max_results=max_results)
    return f"Found {len(results)} results for '{query}'"

# Async caching for research operations
_research_cache: Dict[str, Any] = {}

async def conduct_research_cached(query: str, cache_ttl_minutes: int = 30) -> Optional[str]:
    """Conduct research with caching and TTL."""
    cache_key = f"research_{hash(query)}"
    
    # Check cache validity
    if cache_key in _research_cache:
        cached_data, timestamp = _research_cache[cache_key]
        if datetime.now() - timestamp < timedelta(minutes=cache_ttl_minutes):
            return cached_data
        else:
            del _research_cache[cache_key]
    
    try:
        # Perform research
        researcher = GPTResearcher(query=query)
        context = await researcher.conduct_research()
        report = await researcher.write_report()
        
        # Cache the result
        _research_cache[cache_key] = (report, datetime.now())
        return report
        
    except Exception as e:
        logger.error(f"Research failed for query '{query}': {e}")
        return None
```

---

## **Streamlit & Python UI Best Practices (Updated 2024)**

- **State Management**:
  - Use `st.session_state` for persistent data across reruns
  - Initialize state variables with default values using `.get()` method
  - Use `st.query_params` for shareable URLs and navigation state
  - Clear state appropriately to prevent memory leaks

- **Components**:
  - Keep UI components small and focused
  - ❌ No business logic inside UI code → move to `gpt_researcher/`
  - Keep main Streamlit files thin (presentation only)
  - Use `st.fragment` for partial page updates

- **Performance (Latest API)**:
  - Use `@st.cache_data` for data processing functions and API calls
  - Use `@st.cache_resource` for connections, models, and LLM clients
  - Add TTL (time-to-live) parameters for automatic cache invalidation
  - Use `show_spinner=False` for custom loading control
  - Minimize API calls on every rerun with proper caching
  - Show loading spinners for long operations with `st.spinner()`

### Modern Session State Patterns

```python
import streamlit as st

# Modern initialization with query params
def init_session_state():
    """Initialize session state with query parameter integration."""
    # Get default from query params or use fallback
    if 'selected_country' not in st.session_state:
        st.session_state.selected_country = st.query_params.get("country", "United States")
    
    if 'model_selection' not in st.session_state:
        st.session_state.model_selection = st.query_params.get("model", "gpt-4o-mini")
    
    # Initialize collections safely
    if 'themes' not in st.session_state:
        st.session_state.themes = []
    
    if 'processing_state' not in st.session_state:
        st.session_state.processing_state = "idle"

# Sync UI state with URL for shareable links
def sync_query_params():
    """Sync important state with query parameters."""
    st.query_params.country = st.session_state.selected_country
    st.query_params.model = st.session_state.model_selection

# Use fragments for partial updates
@st.fragment
def display_live_metrics():
    """Update metrics without full page reload."""
    if 'token_usage' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tokens Used", st.session_state.token_usage)
        with col2:
            cost = st.session_state.token_usage * 0.00002  # Example rate
            st.metric("Cost", f"${cost:.4f}")
```

### LangChain Best Practices (Latest API)

- **Agent Creation (Modern Pattern)**:
  - Use `create_tool_calling_agent()` for modern agent architecture
  - Implement proper tool validation with Pydantic models
  - Use `AgentExecutor` for reliable execution with error handling
  - Cache agent executors as resources for performance

- **Tool Integration**:
  - Use `@tool` decorator for simple function-to-tool conversion
  - Implement proper input validation with type hints and docstrings
  - Use `RunnableToTool` for converting complex chains to tools
  - Handle tool errors gracefully with try-catch patterns

- **Model Context Protocol (MCP) Integration**:
  - Use standardized tool interfaces for external integrations
  - Implement proper resource caching for MCP connections
  - Follow MCP patterns for consistent tool behavior
  - Cache MCP servers and connections as Streamlit resources

### Modern LangChain Agent Patterns

```python
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import CallbackManager, BaseCallbackHandler
import streamlit as st

@tool
def search_research_content(country: str, topic: str = "") -> str:
    """Search for research content in a specific domain."""
    try:
        from gpt_researcher.retrievers.tavily import TavilySearch
        search = TavilySearch()
        results = search.search(f"{topic} {country}", max_results=5)
        if topic:
            # Filter results by topic
            filtered = [r for r in results if topic.lower() in r.get('title', '').lower()]
            return f"Research for '{topic}' in {country}: {filtered}"
        return f"Top research results in {country}: {results[:5]}"
    except Exception as e:
        return f"Error fetching research: {str(e)}"

@tool
def search_documents(query: str, domain: str) -> str:
    """Search document store for relevant content."""
    try:
        from gpt_researcher.document import DocumentLoader
        loader = DocumentLoader()
        results = loader.search_documents(query, domain)
        return f"Found {len(results)} documents for '{query}' in {domain}"
    except Exception as e:
        return f"Error searching documents: {str(e)}"

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback for displaying agent progress in Streamlit."""
    
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.steps = []
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        tool_name = serialized.get("name", "Unknown")
        self.steps.append(f"🔧 Using tool: {tool_name}")
        self.placeholder.write("\\n".join(self.steps))
    
    def on_tool_end(self, output, **kwargs):
        self.steps.append(f"✅ Tool completed")
        self.placeholder.write("\\n".join(self.steps))

@st.cache_resource
def create_trends_agent(model_name: str = "gpt-4o-mini"):
    """Create and cache a trends analysis agent."""
    llm = ChatOpenAI(model=model_name, temperature=0.1)
    tools = [search_research_content, search_documents]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a social media trends analyst. Use the available tools to:
        1. Search for current research trends in the specified domain
        2. Find relevant documents and content from various sources
        3. Provide actionable insights for content creation
        
        Always cite your sources and provide specific recommendations."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate"
    )

def run_trends_analysis(query: str, country: str, model: str):
    """Run trends analysis with proper error handling and progress tracking."""
    progress_placeholder = st.empty()
    
    try:
        # Create callback handler for progress tracking
        callback_handler = StreamlitCallbackHandler(progress_placeholder)
        
        # Get cached agent
        agent_executor = create_trends_agent(model)
        
        # Run analysis with progress tracking
        with st.spinner("Analyzing trends..."):
            result = agent_executor.invoke(
                {"input": f"Analyze trends for '{query}' in {country}"},
                config={"callbacks": [callback_handler]}
            )
        
        progress_placeholder.empty()  # Clear progress display
        return result.get("output", "No analysis available")
        
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"Analysis failed: {str(e)}")
        return None

# Usage in Streamlit UI
def display_agent_interface():
    """Modern agent interface with proper state management."""
    st.header("🤖 AI Trends Analyst")
    
    col1, col2 = st.columns(2)
    with col1:
        query = st.text_input("Analysis Query", placeholder="Enter your analysis request...")
    with col2:
        country = st.selectbox("Country", options=list(country_options.keys()))
    
    model = st.selectbox("AI Model", ["gpt-4o", "gpt-4o-mini", "claude-3-sonnet"])
    
    if st.button("🚀 Analyze Trends", type="primary", disabled=not query):
        result = run_trends_analysis(query, country, model)
        if result:
            st.success("Analysis Complete!")
            st.markdown("### 📊 Analysis Results")
            st.markdown(result)
            
            # Store result in session state for reuse
            st.session_state.last_analysis = {
                "query": query,
                "country": country,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
```

### MCP Integration Patterns

```python
# Model Context Protocol integration for external tools
import streamlit as st
from typing import Any, Dict

@st.cache_resource
def get_mcp_client(server_name: str):
    """Cache MCP server connections."""
    # This would connect to external MCP servers
    # Implementation depends on specific MCP server setup
    pass

@tool  
def mcp_tool_wrapper(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Wrapper for MCP tools with error handling."""
    try:
        client = get_mcp_client("social-media-mcp")
        result = client.call_tool(tool_name, parameters)
        return str(result)
    except Exception as e:
        return f"MCP tool error: {str(e)}"
```  

---

## **Folder Structure**

### Research Agent Local Project Structure

```
research-agent-local/
├── gpt_researcher/                 # Core research engine
│   ├── agent.py                   # Main GPTResearcher class
│   ├── prompts.py                 # LLM prompt templates
│   ├── actions/                   # Core research actions
│   │   ├── retriever.py           # Search provider management
│   │   ├── query_processing.py    # Query planning and processing
│   │   ├── web_scraping.py        # Content extraction
│   │   └── report_generation.py   # Report writing and formatting
│   ├── config/                    # Configuration system
│   │   ├── config.py              # Main configuration class
│   │   └── variables/             # Default and custom settings
│   ├── skills/                    # Specialized research skills
│   │   ├── researcher.py          # Research orchestration
│   │   ├── writer.py              # Report generation
│   │   ├── context_manager.py     # Context and memory management
│   │   └── deep_research.py       # Advanced research strategies
│   ├── retrievers/                # Search API integrations
│   │   ├── tavily/                # Tavily Search API
│   │   ├── google/                # Google Custom Search
│   │   ├── bing/                  # Microsoft Bing API
│   │   └── duckduckgo/            # DuckDuckGo search
│   ├── scraper/                   # Web content extraction
│   │   ├── bs/                    # BeautifulSoup scraper
│   │   ├── firecrawl/             # Firecrawl integration
│   │   └── tavily_extract/        # Tavily extract API
│   ├── llm_provider/              # LLM model management
│   ├── mcp/                       # Model Context Protocol integration
│   ├── document/                  # Document processing
│   ├── memory/                    # Memory and context storage
│   └── vector_store/              # Vector database integration
├── multi_agents/                   # Multi-agent coordination system
│   ├── agents/                    # Specialized agent implementations
│   │   ├── researcher.py          # Research execution agent
│   │   ├── writer.py              # Content writing agent
│   │   ├── editor.py              # Workflow coordination agent
│   │   ├── reviewer.py            # Quality assurance agent
│   │   ├── reviser.py             # Content refinement agent
│   │   ├── publisher.py           # Report formatting agent
│   │   └── orchestrator.py        # Chief editor (main coordinator)
│   ├── memory/                    # Shared memory for multi-agents
│   └── main.py                    # Multi-agent system entry point
├── backend/                       # FastAPI web server
│   ├── server/                    # Core server implementation
│   │   ├── app.py                 # Main FastAPI application
│   │   ├── websocket_manager.py   # WebSocket communication
│   │   └── server_utils.py        # Utility functions
│   ├── chat/                      # Chat functionality
│   ├── memory/                    # Conversation memory
│   ├── report_type/               # Specialized report types
│   │   ├── basic_report/          # Standard research reports
│   │   ├── detailed_report/       # Comprehensive reports
│   │   └── deep_research/         # Deep research implementation
│   └── utils.py                   # Backend utilities
├── frontend/                      # Web interface
│   ├── index.html                 # Main HTML interface
│   ├── scripts.js                 # Frontend JavaScript
│   ├── styles.css                 # CSS styling
│   └── nextjs/                    # Next.js React interface (optional)
│       ├── components/            # React components
│       ├── pages/                 # Next.js pages
│       └── config/                # Frontend configuration
├── main.py                        # Primary server entry point
├── cli.py                         # Command-line interface
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Poetry configuration
└── docs/                          # Documentation and examples
    ├── docs/                      # API documentation
    └── examples/                   # Usage examples
```

### **Key Principles**

- **Modular Architecture**: Clear separation between research engine, agents, backend, and frontend
- **Skill-Based Design**: Research capabilities organized as specialized skills
- **Multi-Agent Coordination**: Specialized agents for different aspects of research workflow
- **API-First Approach**: FastAPI backend provides RESTful and WebSocket APIs
- **Flexible Frontend**: Support for both HTML/JS and React-based interfaces
- **Configuration Management**: Centralized configuration with environment variable support
- **Extensible Integrations**: Plugin architecture for search providers, scrapers, and LLM models

### **Configuration Pattern**

```python
# gpt_researcher/config/variables/default.py
DEFAULT_CONFIG = {
    "RETRIEVER": "tavily",
    "FAST_LLM": "openai:gpt-4o-mini", 
    "SMART_LLM": "openai:gpt-4o",
    "STRATEGIC_LLM": "openai:o4-mini",
    "EMBEDDING": "openai:text-embedding-3-small",
    "REPORT_FORMAT": "APA",
    "MAX_SEARCH_RESULTS_PER_QUERY": 5,
    # ... more configuration options
}

# Environment variable override pattern
# .env file or environment variables override defaults
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
RETRIEVER=tavily,mcp  # Enable multiple retrievers
```

---

## **Validation with Pydantic**

Pydantic is the **standard validation library** for:  

- API input validation  
- API output validation  
- LLM response validation  
- Configuration validation  

### Example: Shared `models.py`

```python
# gpt_researcher/models.py
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class ResearchResult(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    source_url: str = Field(..., description="URL of the source")
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class ResearchQuery(BaseModel):
    query: str
    report_type: str = "research_report"
    report_source: str = "web"
    max_results: int = Field(default=10, ge=1, le=50)
    
class ReportRequest(BaseModel):
    query: str
    report_type: str
    language: Optional[str] = "English"
    output_format: str = Field(default="markdown", regex="^(markdown|pdf|docx)$")
```

### Service Usage

```python
# gpt_researcher/skills/researcher.py
from .models import ResearchResult, ResearchQuery

def process_search_results(raw_results: List[dict], query: str) -> List[ResearchResult]:
    """Process and validate search results."""
    validated_results = []
    for result_data in raw_results:
        try:
            result = ResearchResult(**result_data)
            validated_results.append(result)
        except ValidationError as e:
            logger.warning(f"Invalid search result: {e}")
            continue
    
    return validated_results
```

### FastAPI Interface Usage

```python
# backend/server/app.py
from gpt_researcher.models import ReportRequest

@app.post("/research")
async def create_research(request: ReportRequest):
    try:
        # Process validated request
        researcher = GPTResearcher(
            query=request.query,
            report_type=request.report_type,
            report_source="web"
        )
        return await researcher.conduct_research()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
```

### LLM Response Validation Example

```python
# gpt_researcher/actions/report_generation.py
from pydantic import BaseModel, ValidationError
from typing import List

class LLMReportResponse(BaseModel):
    title: str
    introduction: str
    sections: List[str]
    conclusion: str
    confidence: float

def validate_llm_response(raw_response: str) -> LLMReportResponse:
    """Validate and parse LLM JSON response."""
    try:
        data = json.loads(raw_response)
        return LLMReportResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Invalid LLM response: {e}")
        raise ValueError("LLM returned invalid response format")
```

---

### Best Practices

- Always use Pydantic models for data validation
- Use `Field()` for additional constraints and documentation
- Add custom validators with `@validator` for complex validation logic
- Handle `ValidationError` exceptions gracefully
- Use type hints consistently with Pydantic models
- For configuration → validate environment variables with Pydantic settings

---

## Common Gotchas

1. **Virtual Environment**: Always activate virtual environment before running scripts
2. **Environment Variables**: Ensure all required API keys are properly set in environment
3. **Configuration Files**: Use `gpt_researcher/config/` for configuration management
4. **Package Dependencies**: Maintain `requirements.txt` and `pyproject.toml` for dependencies
5. **Shared Code**: Core functionality lives in `gpt_researcher/` package
6. **API Rate Limits**: Search APIs have rate limits - implement proper retry logic
7. **MCP Integration**: Ensure MCP servers are properly configured and accessible
8. **Vector Store**: Qdrant configuration for semantic search and context retrieval
9. **Multi-Agent Coordination**: Ensure proper LangGraph workflow configuration
10. **WebSocket Connections**: Handle WebSocket lifecycle properly for real-time updates

---

## **AI-Assisted Development Best Practices**

- Be explicit with requirements when prompting AI
- Use XML tags for structured prompts
- Chain complex tasks into smaller ones
- Always validate AI output with Pydantic
- Treat AI code as **drafts** → always review, test, and refactor
- Use AI for:

  - Test generation
  - Documentation
  - Code explanations
  - Refactoring suggestions

---

## **Golden Rules**

- ✅ Extend existing code before writing new code
- ✅ Validate everything (input, output, LLM) with Pydantic
- ✅ Keep concerns separated (UI, business logic, data processing)
- ✅ Always prioritize readability, maintainability, and security
- ❌ Never mix business logic with UI components
- ❌ Never push unvalidated AI code directly

---

## ✅ Do & ❌ Don’t Quick Reference

| Area                  | ✅ Do                                                                 | ❌ Don’t                                              |
|-----------------------|---------------------------------------------------------------------|------------------------------------------------------|
| **Project Setup**     | Use **virtual environments** with `pip`                             | Use global installs or `conda` without approval      |
| **Logging**           | Use Python's **`logging`** module                                   | Use `print()` directly for debugging                 |
| **File Creation**     | Extend existing modules when possible                               | Create new files, APIs, or scripts without approval  |
| **API Design**        | Extend existing API wrappers                                        | Create redundant API integrations                    |
| **Imports**           | Use top-level `import` statements                                   | Use dynamic `importlib.import_module()` inside funcs |
| **Validation**        | Validate **input/output/LLM** with Pydantic models                  | Trust raw input/output/LLM responses                 |
| **Code Reuse**        | Share models via `gpt_researcher/` package                          | Duplicate models across components                    |
| **Error Handling**    | Use specific exception types with proper handling                   | Use bare `except:` or ignore errors silently        |
| **Functions**         | Keep ≤ 20 lines, ≤ 3–4 params, single responsibility                | Write long, multi-purpose functions                  |
| **FastAPI Endpoints** | Keep API logic separate from business logic                         | Mix research processing with API endpoints           |
| **Configuration**     | Use environment variables via `gpt_researcher/config/`              | Hard-code API keys or configuration values           |
| **Research Engine**   | Configure research workflows via `gpt_researcher/` modules          | Duplicate research logic across different components |
| **Shared Code**       | Place reusable logic in `gpt_researcher/` package                   | Duplicate business logic across agents                |
| **LLM Integration**   | Always validate schema with Pydantic before using response          | Use raw LLM strings directly in business logic       |
| **Search APIs**       | Use wrapper classes with rate limiting and error handling           | Call search APIs directly without abstraction        |
| **Token Tracking**    | Monitor costs with proper cost callback implementations             | Ignore token usage and costs                          |
| **Dependencies**      | Use `requirements.txt` and `pyproject.toml` with pinned versions   | Install packages without version control              |
| **Async Operations**  | Use proper `async/await` patterns for I/O operations               | Use synchronous calls for network operations         |
| **WebSocket**         | Handle WebSocket lifecycle and error states properly               | Ignore WebSocket connection management                |
| **LangGraph Agents**  | Use proper state management and workflow coordination              | Create agents without proper state handling          |
| **MCP Integration**   | Cache MCP connections and handle errors gracefully                 | Create MCP connections on every request              |
| **Vector Storage**    | Use Qdrant for semantic search and context retrieval               | Store context without semantic organization          |
| **Multi-Agent**       | Coordinate agents through proper workflow orchestration            | Run agents independently without coordination        |
| **Report Generation** | Use proper formatting and citation management                       | Generate reports without proper structure             |
| **Data Models**       | Use Pydantic models for all structured data                         | Use plain dictionaries for complex data structures   |

---

🔥 **Golden Takeaway**:  
> **Extend existing code, validate everything with Pydantic, keep UI and business logic separate, and never trust unvalidated input or AI output.**
