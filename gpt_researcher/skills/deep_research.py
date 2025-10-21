from typing import List, Dict, Any, Optional, Set
import asyncio
import logging
import time
from datetime import datetime, timedelta
import json_repair

from gpt_researcher.llm_provider.generic.base import ReasoningEfforts
from ..utils.llm import create_chat_completion
from ..utils.enum import ReportType, ReportSource, Tone
from ..actions.query_processing import get_search_results
from ..skills.researcher import ResearchConductor

logger = logging.getLogger(__name__)

# Maximum words allowed in context (25k words for safety margin)
MAX_CONTEXT_WORDS = 25000


def count_words(text: str) -> int:
    """Count words in a text string"""
    return len(text.split())


def trim_context_to_word_limit(context_list: List[str], max_words: int = MAX_CONTEXT_WORDS) -> List[str]:
    """Trim context list to stay within word limit while preserving most recent/relevant items"""
    total_words = 0
    trimmed_context = []

    # Process in reverse to keep most recent items
    for item in reversed(context_list):
        words = count_words(item)
        if total_words + words <= max_words:
            # Insert at start to maintain original order
            trimmed_context.insert(0, item)
            total_words += words
        else:
            break

    return trimmed_context


class ResearchProgress:
    def __init__(self, total_depth: int, total_breadth: int):
        self.current_depth = 1  # Start from 1 and increment up to total_depth
        self.total_depth = total_depth
        # Start from 0 and count up to total_breadth as queries complete
        self.current_breadth = 0
        self.total_breadth = total_breadth
        self.current_query: Optional[str] = None
        self.total_queries = 0
        self.completed_queries = 0


class DeepResearchSkill:
    def __init__(self, researcher):
        self.researcher = researcher
        self.breadth = getattr(researcher.cfg, 'deep_research_breadth', 4)
        self.depth = getattr(researcher.cfg, 'deep_research_depth', 2)
        self.concurrency_limit = getattr(
            researcher.cfg, 'deep_research_concurrency', 2)
        self.websocket = researcher.websocket
        self.tone = researcher.tone
        self.config_path = researcher.cfg.config_path if hasattr(
            researcher.cfg, 'config_path') else None
        self.headers = researcher.headers or {}
        self.visited_urls = researcher.visited_urls
        self.learnings = []
        self.research_sources = []  # Track all research sources
        self.context = []  # Track all context

    async def extract_keywords_from_query(self, query: str, max_keywords: int = 100) -> List[str]:
        """
        Extract up to 100 keywords from the research query.

        Args:
            query: The research query/prompt
            max_keywords: Maximum number of keywords to extract (default: 100)

        Returns:
            List of extracted keywords
        """
        extraction_prompt = f"""Analyze the following research query and extract up to {max_keywords} relevant keywords and key phrases.

Include:
- Main topics and concepts
- Specific entities (companies, products, technologies, locations, people)
- Technical terms and industry-specific vocabulary
- Related domains and fields
- Time periods or dates if mentioned
- Quantitative metrics or specifications

Return ONLY a JSON array of strings (keywords), nothing else.

Query:
{query[:5000]}

Keywords (JSON array):"""

        try:
            response = await create_chat_completion(
                model=self.researcher.cfg.strategic_llm_model,
                messages=[{"role": "user", "content": extraction_prompt}],
                llm_provider=self.researcher.cfg.strategic_llm_provider,
                temperature=0.3,
                max_tokens=2000,
                reasoning_effort=ReasoningEfforts.Low.value,
                llm_kwargs=self.researcher.cfg.llm_kwargs,
            )

            # Parse JSON response
            keywords = json_repair.loads(response)

            if isinstance(keywords, list):
                # Limit to max_keywords
                keywords = keywords[:max_keywords]
                logger.info(f"Extracted {len(keywords)} keywords from query")
                return keywords
            else:
                logger.warning(
                    f"Invalid keyword extraction response: {response[:200]}")
                return self._fallback_keyword_extraction(query, max_keywords)

        except Exception as e:
            logger.warning(f"Failed to extract keywords via LLM: {e}")
            return self._fallback_keyword_extraction(query, max_keywords)

    def _fallback_keyword_extraction(self, query: str, max_keywords: int) -> List[str]:
        """Fallback keyword extraction using simple text processing"""
        # Remove markdown formatting
        clean_text = query.replace('#', '').replace('*', '').replace('`', '')

        # Split into words and filter
        words = clean_text.split()

        # Filter out common words, very short words, and URLs
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                      'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}

        keywords = []
        for word in words:
            # Skip if too short, is URL, or is stop word
            if len(word) <= 2 or word.startswith('http') or word.lower() in stop_words:
                continue
            # Clean punctuation
            clean_word = word.strip('.,;:!?()[]{}"\'-')
            if clean_word:
                keywords.append(clean_word)

        # Return unique keywords up to max_keywords
        unique_keywords = list(dict.fromkeys(keywords))
        logger.info(
            f"Fallback extraction: {len(unique_keywords[:max_keywords])} keywords")
        return unique_keywords[:max_keywords]

    async def group_keywords_into_topics(self, keywords: List[str], num_groups: int = None) -> Dict[str, List[str]]:
        """
        Group keywords into logical topic clusters.

        Args:
            keywords: List of keywords to group
            num_groups: Number of groups to create (auto-determined if None)

        Returns:
            Dictionary mapping topic names to lists of keywords
        """
        if not keywords:
            return {}

        # Auto-determine number of groups based on keyword count
        if num_groups is None:
            if len(keywords) <= 20:
                num_groups = 3
            elif len(keywords) <= 50:
                num_groups = 5
            elif len(keywords) <= 80:
                num_groups = 8
            else:
                num_groups = 10

        grouping_prompt = f"""Analyze these {len(keywords)} keywords and organize them into {num_groups} logical topic groups.

Keywords:
{', '.join(keywords)}

Create coherent topic groups where each group has:
1. A clear, descriptive topic name (2-5 words)
2. Related keywords that belong together conceptually

Return ONLY a JSON object where:
- Keys are topic names
- Values are arrays of keywords from the list above

Example format:
{{
  "Manufacturing Facilities": ["factory", "production", "manufacturing", "facility"],
  "Supply Chain": ["supplier", "logistics", "delivery", "procurement"],
  ...
}}

Topic Groups (JSON object):"""

        try:
            response = await create_chat_completion(
                model=self.researcher.cfg.strategic_llm_model,
                messages=[{"role": "user", "content": grouping_prompt}],
                llm_provider=self.researcher.cfg.strategic_llm_provider,
                temperature=0.4,
                max_tokens=3000,
                reasoning_effort=ReasoningEfforts.Medium.value,
                llm_kwargs=self.researcher.cfg.llm_kwargs,
            )

            # Parse JSON response
            groups = json_repair.loads(response)

            if isinstance(groups, dict):
                logger.info(
                    f"Grouped {len(keywords)} keywords into {len(groups)} topics")
                return groups
            else:
                logger.warning(f"Invalid grouping response: {response[:200]}")
                return self._fallback_keyword_grouping(keywords, num_groups)

        except Exception as e:
            logger.warning(f"Failed to group keywords via LLM: {e}")
            return self._fallback_keyword_grouping(keywords, num_groups)

    def _fallback_keyword_grouping(self, keywords: List[str], num_groups: int) -> Dict[str, List[str]]:
        """Fallback keyword grouping - simple chunking"""
        groups = {}
        chunk_size = max(1, len(keywords) // num_groups)

        for i in range(num_groups):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < num_groups - \
                1 else len(keywords)
            group_keywords = keywords[start_idx:end_idx]

            if group_keywords:
                # Use first keyword as topic name
                topic_name = f"Topic {i+1}: {group_keywords[0]}"
                groups[topic_name] = group_keywords

        logger.info(f"Fallback grouping: {len(groups)} groups created")
        return groups

    async def generate_search_queries(self, query: str, num_queries: int = 3) -> List[Dict[str, str]]:
        """Generate SERP queries for research"""
        messages = [
            {"role": "system", "content": "You are an expert researcher generating search queries."},
            {"role": "user",
             "content": f"""Given the following prompt, generate {num_queries} unique search queries to research the topic thoroughly.

CRITICAL REQUIREMENTS:
- Each search query MUST be concise and focused (maximum 10-15 words)
- Extract ONLY the essential keywords from the prompt
- DO NOT include lengthy instructions or context in the query
- Search engines require SHORT, targeted queries

For each query, provide a research goal. Format as 'Query: <query>' followed by 'Goal: <goal>' for each pair.

Prompt: {query}"""}
        ]

        response = await create_chat_completion(
            messages=messages,
            llm_provider=self.researcher.cfg.strategic_llm_provider,
            model=self.researcher.cfg.strategic_llm_model,
            reasoning_effort=self.researcher.cfg.reasoning_effort,
            temperature=0.4
        )

        lines = response.split('\n')
        queries = []
        current_query = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Query:'):
                if current_query:
                    queries.append(current_query)
                # Extract query and truncate if needed
                query_text = line.replace('Query:', '').strip()
                # Hard limit: truncate to 1024 characters
                MAX_QUERY_LENGTH = 1024
                if len(query_text) > MAX_QUERY_LENGTH:
                    logger.warning(
                        f"Deep research query truncated from {len(query_text)} to {MAX_QUERY_LENGTH} characters"
                    )
                    query_text = query_text[:MAX_QUERY_LENGTH].strip()
                current_query = {'query': query_text}
            elif line.startswith('Goal:') and current_query:
                current_query['researchGoal'] = line.replace(
                    'Goal:', '').strip()

        if current_query:
            queries.append(current_query)

        return queries[:num_queries]

    async def generate_research_plan(self, query: str, num_questions: int = 3) -> List[str]:
        """Generate follow-up questions to clarify research direction"""
        # Extract keywords from query to avoid sending entire prompt to search engines
        researcher_skill = ResearchConductor(self.researcher)
        search_keywords = await researcher_skill._extract_search_keywords(query, max_words=15)
        logger.info(
            f"Extracted search keywords for research planning: '{search_keywords}'")

        # Get initial search results to inform query generation
        search_results = await get_search_results(search_keywords, self.researcher.retrievers[0], researcher=self.researcher)
        logger.info(
            f"Initial web knowledge obtained: {len(search_results)} results")

        # Get current time for context
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        messages = [
            {"role": "system", "content": "You are an expert researcher. Your task is to analyze the original query and search results, then generate targeted questions that explore different aspects and time periods of the topic."},
            {"role": "user",
             "content": f"""Original query: {query}

Current time: {current_time}

Search results:
{search_results}

Based on these results, the original query, and the current time, generate {num_questions} unique questions. Each question should explore a different aspect or time period of the topic, considering recent developments up to {current_time}.

Format each question on a new line starting with 'Question: '"""}
        ]

        response = await create_chat_completion(
            messages=messages,
            llm_provider=self.researcher.cfg.strategic_llm_provider,
            model=self.researcher.cfg.strategic_llm_model,
            reasoning_effort=ReasoningEfforts.High.value,
            temperature=0.4
        )

        questions = [q.replace('Question:', '').strip()
                     for q in response.split('\n')
                     if q.strip().startswith('Question:')]
        return questions[:num_questions]

    async def process_research_results(self, query: str, context: str, num_learnings: int = 3) -> Dict[str, List[str]]:
        """Process research results to extract learnings and follow-up questions"""
        messages = [
            {"role": "system",
                "content": "You are an expert researcher analyzing search results."},
            {"role": "user",
             "content": f"Given the following research results for the query '{query}', extract key learnings and suggest follow-up questions. For each learning, include a citation to the source URL if available. Format each learning as 'Learning [source_url]: <insight>' and each question as 'Question: <question>':\n\n{context}"}
        ]

        response = await create_chat_completion(
            messages=messages,
            llm_provider=self.researcher.cfg.strategic_llm_provider,
            model=self.researcher.cfg.strategic_llm_model,
            temperature=0.4,
            reasoning_effort=ReasoningEfforts.High.value,
            max_tokens=1000
        )

        lines = response.split('\n')
        learnings = []
        questions = []
        citations = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Learning'):
                import re
                url_match = re.search(r'\[(.*?)\]:', line)
                if url_match:
                    url = url_match.group(1)
                    learning = line.split(':', 1)[1].strip()
                    learnings.append(learning)
                    citations[learning] = url
                else:
                    # Try to find URL in the line itself
                    url_match = re.search(
                        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
                    if url_match:
                        url = url_match.group(0)
                        learning = line.replace(url, '').replace(
                            'Learning:', '').strip()
                        learnings.append(learning)
                        citations[learning] = url
                    else:
                        learnings.append(line.replace('Learning:', '').strip())
            elif line.startswith('Question:'):
                questions.append(line.replace('Question:', '').strip())

        return {
            'learnings': learnings[:num_learnings],
            'followUpQuestions': questions[:num_learnings],
            'citations': citations
        }

    async def deep_research(
            self,
            query: str,
            breadth: int,
            depth: int,
            learnings: List[str] = None,
            citations: Dict[str, str] = None,
            visited_urls: Set[str] = None,
            on_progress=None
    ) -> Dict[str, Any]:
        """Conduct deep iterative research"""
        if learnings is None:
            learnings = []
        if citations is None:
            citations = {}
        if visited_urls is None:
            visited_urls = set()

        progress = ResearchProgress(depth, breadth)

        if on_progress:
            on_progress(progress)

        # Generate search queries
        serp_queries = await self.generate_search_queries(query, num_queries=breadth)
        progress.total_queries = len(serp_queries)

        all_learnings = learnings.copy()
        all_citations = citations.copy()
        all_visited_urls = visited_urls.copy()
        all_context = []
        all_sources = []

        # Process queries with concurrency limit
        semaphore = asyncio.Semaphore(self.concurrency_limit)

        async def process_query(serp_query: Dict[str, str]) -> Optional[Dict[str, Any]]:
            async with semaphore:
                try:
                    progress.current_query = serp_query['query']
                    if on_progress:
                        on_progress(progress)

                    from .. import GPTResearcher
                    researcher = GPTResearcher(
                        query=serp_query['query'],
                        report_type=ReportType.ResearchReport.value,
                        report_source=ReportSource.Web.value,
                        tone=self.tone,
                        websocket=self.websocket,
                        config_path=self.config_path,
                        headers=self.headers,
                        visited_urls=self.visited_urls
                    )

                    # Conduct research
                    logger.info(
                        f"Sub-researcher conducting research for: {serp_query['query']}")
                    context = await researcher.conduct_research()
                    logger.info(
                        f"Sub-researcher completed. Context length: {len(str(context)) if context else 0} chars")

                    # Get results and visited URLs
                    visited = researcher.visited_urls
                    sources = researcher.research_sources

                    logger.info(
                        f"Sub-researcher visited {len(visited)} URLs, collected {len(sources)} sources")

                    # Process results to extract learnings and citations
                    results = await self.process_research_results(
                        query=serp_query['query'],
                        context=context
                    )

                    # Update progress
                    progress.completed_queries += 1
                    progress.current_breadth += 1
                    if on_progress:
                        on_progress(progress)

                    return {
                        'learnings': results['learnings'],
                        'visited_urls': list(visited),
                        'followUpQuestions': results['followUpQuestions'],
                        'researchGoal': serp_query['researchGoal'],
                        'citations': results['citations'],
                        'context': context if context else "",
                        'sources': sources if sources else []
                    }

                except Exception as e:
                    logger.error(
                        f"Error processing query '{serp_query['query']}': {str(e)}")
                    return None

        # Process queries concurrently with limit
        tasks = [process_query(query) for query in serp_queries]
        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]

        # Update breadth progress based on successful queries
        progress.current_breadth = len(results)
        if on_progress:
            on_progress(progress)

        # Collect all results
        for result in results:
            all_learnings.extend(result['learnings'])
            all_visited_urls.update(result['visited_urls'])
            all_citations.update(result['citations'])
            if result['context']:
                all_context.append(result['context'])
            if result['sources']:
                all_sources.extend(result['sources'])

            # Continue deeper if needed
            if depth > 1:
                new_breadth = max(2, breadth // 2)
                new_depth = depth - 1
                progress.current_depth += 1

                # Create next query from research goal and follow-up questions
                next_query = f"""
                Previous research goal: {result['researchGoal']}
                Follow-up questions: {' '.join(result['followUpQuestions'])}
                """

                # Recursive research
                deeper_results = await self.deep_research(
                    query=next_query,
                    breadth=new_breadth,
                    depth=new_depth,
                    learnings=all_learnings,
                    citations=all_citations,
                    visited_urls=all_visited_urls,
                    on_progress=on_progress
                )

                all_learnings = deeper_results['learnings']
                all_visited_urls.update(deeper_results['visited_urls'])
                all_citations.update(deeper_results['citations'])
                if deeper_results.get('context'):
                    all_context.extend(deeper_results['context'])
                if deeper_results.get('sources'):
                    all_sources.extend(deeper_results['sources'])

        # Update class tracking
        self.context.extend(all_context)
        self.research_sources.extend(all_sources)

        # Trim context to stay within word limits
        trimmed_context = trim_context_to_word_limit(all_context)
        logger.info(
            f"Trimmed context from {len(all_context)} items to {len(trimmed_context)} items to stay within word limit")

        return {
            'learnings': list(set(all_learnings)),
            'visited_urls': list(all_visited_urls),
            'citations': all_citations,
            'context': trimmed_context,
            'sources': all_sources
        }

    async def run(self, on_progress=None) -> str:
        """Run the deep research process and generate final report"""
        start_time = time.time()

        # Log initial costs
        initial_costs = self.researcher.get_costs()

        follow_up_questions = await self.generate_research_plan(self.researcher.query)
        answers = ["Automatically proceeding with research"] * \
            len(follow_up_questions)

        qa_pairs = [f"Q: {q}\nA: {a}" for q,
                    a in zip(follow_up_questions, answers)]
        combined_query = f"""
        Initial Query: {self.researcher.query}\nFollow - up Questions and Answers:\n
        """ + "\n".join(qa_pairs)

        # Use keyword-based deep research instead of raw query
        results = await self.keyword_based_deep_research(
            query=combined_query,
            on_progress=on_progress
        )

        # Get costs after deep research
        research_costs = self.researcher.get_costs() - initial_costs

        # Log research costs if we have a log handler
        if self.researcher.log_handler:
            await self.researcher._log_event("research", step="deep_research_costs", details={
                "research_costs": research_costs,
                "total_costs": self.researcher.get_costs()
            })

        # Prepare context with citations
        context_with_citations = []
        for learning in results['learnings']:
            citation = results['citations'].get(learning, '')
            if citation:
                context_with_citations.append(
                    f"{learning} [Source: {citation}]")
            else:
                context_with_citations.append(learning)

        # Add all research context
        if results.get('context'):
            context_with_citations.extend(results['context'])

        # Trim final context to word limit
        final_context = trim_context_to_word_limit(context_with_citations)

        # Set enhanced context and visited URLs
        self.researcher.context = "\n".join(final_context)
        self.researcher.visited_urls = results['visited_urls']

        # Set research sources
        if results.get('sources'):
            self.researcher.research_sources = results['sources']

        # Log total execution time
        end_time = time.time()
        execution_time = timedelta(seconds=end_time - start_time)
        logger.info(f"Total research execution time: {execution_time}")
        logger.info(f"Total research costs: ${research_costs:.2f}")

        # Return the context - don't generate report here as it will be done by the main agent
        return self.researcher.context

    async def keyword_based_deep_research(
            self,
            query: str,
            on_progress=None
    ) -> Dict[str, Any]:
        """
        NEW: Conduct deep research using keyword extraction and grouping.

        Workflow:
        1. Extract up to 100 keywords from the query
        2. Group keywords into logical topic clusters
        3. Conduct focused sub-searches for each topic group
        4. Aggregate and synthesize results

        Args:
            query: The research query/prompt
            on_progress: Optional progress callback

        Returns:
            Dictionary containing:
                - learnings: List of key findings
                - visited_urls: List of URLs visited
                - citations: Dict mapping learnings to sources
                - context: List of context strings
                - sources: List of source documents
        """
        logger.info("=" * 80)
        logger.info("KEYWORD-BASED DEEP RESEARCH INITIATED")
        logger.info("=" * 80)

        start_time = time.time()
        initial_costs = self.researcher.get_costs()

        # Step 1: Extract keywords
        logger.info("Step 1/4: Extracting keywords from query...")
        keywords = await self.extract_keywords_from_query(query, max_keywords=100)

        if not keywords:
            logger.warning(
                "No keywords extracted, falling back to standard deep research")
            return await self.conduct_deep_research(query, on_progress=on_progress)

        logger.info(f"Extracted {len(keywords)} keywords: {keywords[:20]}...")

        # Step 2: Group keywords into topics
        logger.info("Step 2/4: Grouping keywords into logical topics...")
        keyword_groups = await self.group_keywords_into_topics(keywords)

        if not keyword_groups:
            logger.warning(
                "No keyword groups created, falling back to standard deep research")
            return await self.conduct_deep_research(query, on_progress=on_progress)

        logger.info(f"Created {len(keyword_groups)} topic groups:")
        for topic_name, topic_keywords in keyword_groups.items():
            logger.info(f"  - {topic_name}: {len(topic_keywords)} keywords")

        # Step 3: Conduct sub-searches for each topic group
        logger.info(
            "Step 3/4: Conducting focused searches for each topic group...")

        all_context = []
        all_sources = []
        visited_urls = set()

        # Process each topic group
        semaphore = asyncio.Semaphore(self.concurrency_limit)

        async def research_topic_group(topic_name: str, topic_keywords: List[str]) -> Dict[str, Any]:
            """Research a single topic group"""
            async with semaphore:
                try:
                    # Create focused search query from topic keywords
                    # Use top 10-15 keywords for the search query
                    search_keywords = ' '.join(topic_keywords[:15])

                    logger.info(f"Researching topic: {topic_name}")
                    logger.info(f"  Keywords: {search_keywords}")

                    # Create sub-researcher for this topic
                    from .. import GPTResearcher
                    sub_researcher = GPTResearcher(
                        query=search_keywords,
                        report_type=ReportType.ResearchReport.value,
                        report_source=ReportSource.Web.value,
                        tone=self.tone,
                        websocket=self.websocket,
                        config_path=self.config_path,
                        headers=self.headers,
                        visited_urls=self.visited_urls
                    )

                    # Conduct research for this topic
                    context = await sub_researcher.conduct_research()

                    # Get results
                    sources = getattr(sub_researcher, 'research_sources', [])
                    urls = getattr(sub_researcher, 'visited_urls', set())

                    # Propagate costs from sub-researcher to parent researcher
                    sub_costs = sub_researcher.get_costs()
                    if sub_costs > 0:
                        self.researcher.add_costs(sub_costs)
                        logger.info(
                            f"💸 Topic '{topic_name}' costs: ${sub_costs:.8f}")

                    logger.info(
                        f"Completed research for '{topic_name}': {len(str(context))} chars, {len(sources)} sources")

                    return {
                        'topic': topic_name,
                        'context': context,
                        'sources': sources,
                        'visited_urls': urls,
                        'keywords': topic_keywords
                    }

                except Exception as e:
                    logger.error(
                        f"Error researching topic '{topic_name}': {e}")
                    return {
                        'topic': topic_name,
                        'context': '',
                        'sources': [],
                        'visited_urls': set(),
                        'keywords': topic_keywords
                    }

        # Process all topic groups concurrently
        research_tasks = [
            research_topic_group(topic_name, topic_keywords)
            for topic_name, topic_keywords in keyword_groups.items()
        ]

        topic_results = await asyncio.gather(*research_tasks)

        # Step 4: Aggregate results
        logger.info("Step 4/4: Aggregating and synthesizing results...")

        all_learnings = []
        all_citations = {}

        # Collect all contexts and metadata for Qdrant storage
        contexts_for_qdrant = []
        
        for result in topic_results:
            if result['context']:
                context_str = str(result['context'])
                
                # Store context with topic metadata for Qdrant
                if context_str.strip():
                    contexts_for_qdrant.append({
                        'text': context_str,
                        'topic': result['topic'],
                        'keywords': result.get('keywords', [])
                    })
                
                # Add topic header
                topic_section = f"\n\n## {result['topic']}\n\n{result['context']}"
                all_context.append(topic_section)

                # Extract learnings from context (split into sentences/paragraphs)
                if context_str:
                    # Split by double newlines for paragraphs, or periods for sentences
                    learnings = [s.strip()
                                 for s in context_str.split('\n\n') if s.strip()]
                    all_learnings.extend(learnings)

                    # Create citations mapping (use topic name as source)
                    for learning in learnings:
                        if learning and len(learning) > 10:  # Skip very short items
                            all_citations[learning] = f"Topic: {result['topic']}"

            if result['sources']:
                all_sources.extend(result['sources'])

            if result['visited_urls']:
                visited_urls.update(result['visited_urls'])

        # **PHASE 3 OPTIMIZATION: Use Qdrant for semantic aggregation**
        if self.researcher.qdrant_store and contexts_for_qdrant:
            logger.info("🎯 Phase 3: Using Qdrant for semantic content aggregation...")
            
            if self.websocket:
                from ..actions.utils import stream_output
                await stream_output(
                    "logs",
                    "phase3_optimization",
                    f"🎯 Phase 3: Optimizing content with semantic search across {len(contexts_for_qdrant)} topics...",
                    self.websocket,
                )
            
            try:
                # Store all topic contexts in Qdrant with metadata
                from datetime import datetime
                texts_to_store = [ctx['text'] for ctx in contexts_for_qdrant]
                metadata_to_store = [
                    {
                        'topic': ctx['topic'],
                        'keywords': ', '.join(ctx['keywords'][:10]),
                        'timestamp': datetime.now().isoformat(),
                        'type': 'deep_research_topic',
                        'query': query[:500]  # Store original query (truncated)
                    }
                    for ctx in contexts_for_qdrant
                ]
                
                await self.researcher.store_in_qdrant(texts_to_store, metadata_to_store)
                logger.info(f"✅ Stored {len(texts_to_store)} topic contexts in Qdrant")
                
                if self.websocket:
                    await stream_output(
                        "logs",
                        "qdrant_stored",
                        f"✅ Stored {len(texts_to_store)} research topics in semantic database",
                        self.websocket,
                    )
                
                # Perform semantic search to get most relevant content
                semantic_results = await self.researcher.retrieve_from_qdrant(
                    query,
                    limit=min(len(contexts_for_qdrant) * 3, 20),  # Get top passages across all topics
                    score_threshold=0.5
                )
                
                if semantic_results:
                    logger.info(f"🔍 Retrieved {len(semantic_results)} semantically relevant passages")
                    
                    if self.websocket:
                        await stream_output(
                            "logs",
                            "semantic_search_complete",
                            f"🔍 Found {len(semantic_results)} most relevant passages via semantic search",
                            self.websocket,
                        )
                    
                    # Replace all_context with semantically ranked content
                    semantic_context = []
                    seen_texts = set()  # Deduplicate similar content
                    
                    for idx, result in enumerate(semantic_results, 1):
                        text = result.get('text', '')
                        metadata = result.get('metadata', {})
                        score = result.get('score', 0.0)
                        topic = metadata.get('topic', 'Unknown')
                        
                        # Deduplicate: check if we've seen very similar content
                        text_key = text[:200]  # Use first 200 chars as dedup key
                        if text_key not in seen_texts:
                            seen_texts.add(text_key)
                            semantic_context.append(
                                f"\n## {topic} (Relevance: {score:.2f})\n\n{text}"
                            )
                            
                            # Update citations with relevance score
                            for learning in text.split('\n\n'):
                                if learning.strip() and len(learning) > 10:
                                    all_citations[learning.strip()] = f"Topic: {topic} (Score: {score:.2f})"
                    
                    # Use semantic results if we got good content
                    if semantic_context:
                        all_context = semantic_context
                        logger.info(f"✨ Using {len(semantic_context)} semantically ranked passages (deduplicated)")
                        
                        if self.websocket:
                            await stream_output(
                                "logs",
                                "phase3_complete",
                                f"✨ Phase 3 Complete: {len(semantic_context)} passages ranked by relevance (deduplicated from {len(semantic_results)} results)",
                                self.websocket,
                            )
                    else:
                        logger.info("⚠️ Semantic search returned no content, using original aggregation")
                        
                        if self.websocket:
                            await stream_output(
                                "logs",
                                "phase3_fallback",
                                "⚠️ Semantic search produced no results, using standard aggregation",
                                self.websocket,
                            )
                else:
                    logger.info("ℹ️ No semantic results above threshold, using original aggregation")
                    
                    if self.websocket:
                        await stream_output(
                            "logs",
                            "phase3_no_results",
                            "ℹ️ No content above relevance threshold, using standard aggregation",
                            self.websocket,
                        )
                    
            except Exception as e:
                logger.warning(f"⚠️ Qdrant aggregation failed, falling back to standard aggregation: {e}")
                
                if self.websocket:
                    await stream_output(
                        "logs",
                        "phase3_error",
                        f"⚠️ Phase 3 optimization failed: {str(e)}, using standard aggregation",
                        self.websocket,
                    )
        
        # Trim context to word limit
        final_context = trim_context_to_word_limit(all_context)

        # Update researcher state
        self.researcher.context = "\n".join(final_context)
        self.researcher.visited_urls = visited_urls
        self.researcher.research_sources = all_sources

        # Calculate costs and execution time
        research_costs = self.researcher.get_costs() - initial_costs
        end_time = time.time()
        execution_time = timedelta(seconds=end_time - start_time)

        # Log summary
        logger.info("=" * 80)
        logger.info("KEYWORD-BASED DEEP RESEARCH COMPLETED")
        logger.info(f"  Topics researched: {len(keyword_groups)}")
        logger.info(f"  Total keywords: {len(keywords)}")
        logger.info(f"  Phase 3 optimization: {'Qdrant semantic search' if self.researcher.qdrant_store and contexts_for_qdrant else 'Standard aggregation'}")
        logger.info(f"  Context length: {len(self.researcher.context)} chars")
        logger.info(f"  Context passages: {len(final_context)}")
        logger.info(f"  Sources found: {len(all_sources)}")
        logger.info(f"  URLs visited: {len(visited_urls)}")
        logger.info(f"  Execution time: {execution_time}")
        logger.info(f"  Research costs: ${research_costs:.2f}")
        logger.info("=" * 80)

        # Log event if handler available
        if self.researcher.log_handler:
            await self.researcher._log_event("research", step="keyword_based_deep_research", details={
                "topics_count": len(keyword_groups),
                "keywords_count": len(keywords),
                "phase3_optimization": "qdrant_semantic" if self.researcher.qdrant_store and contexts_for_qdrant else "standard",
                "context_length": len(self.researcher.context),
                "context_passages": len(final_context),
                "sources_count": len(all_sources),
                "urls_visited": len(visited_urls),
                "execution_time": str(execution_time),
                "research_costs": research_costs
            })

        # Return dictionary structure expected by run() method
        return {
            'learnings': list(set(all_learnings)),
            'visited_urls': list(visited_urls),
            'citations': all_citations,
            'context': final_context,
            'sources': all_sources
        }
