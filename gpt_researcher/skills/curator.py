from typing import Dict, Optional, List
import json
import logging
from ..config.config import Config
from ..utils.llm import create_chat_completion
from ..actions import stream_output


class SourceCurator:
    """Ranks sources and curates data based on their relevance, credibility and reliability."""

    def __init__(self, researcher):
        self.researcher = researcher
        self.logger = logging.getLogger(__name__)

    async def curate_sources(
        self,
        source_data,
        max_results: int = None,
    ):
        """
        Rank sources based on research data and guidelines.
        Filter out garbage content like error pages, access denied, installation guides.

        Args:
            source_data: Can be:
                - List of document dictionaries with 'raw_content' or 'content' keys
                - List of LangChain Document objects
                - String context (combined research context)
            max_results: Maximum number of top sources to return (None = NO LIMIT)

        Returns:
            Original source_data format (list, dict, or string) - filtered and curated
        """
        # Handle string context - just return it as-is (already curated during compression)
        if isinstance(source_data, str):
            self.logger.info(
                "Source data is a string context - returning as-is")
            return source_data

        # Handle empty lists or None
        if not source_data:
            self.logger.warning("No source data provided to curator")
            return [] if isinstance(source_data, list) else source_data

        # If max_results is None or 0, use ALL filtered sources (no limit for Qdrant)
        if max_results is None or max_results == 0:
            max_results = len(source_data) if isinstance(
                source_data, list) else 10
        else:
            # Use config value if max_results not provided
            max_results = getattr(
                self.researcher.cfg, 'max_context_results_per_query', max_results)
            if max_results is None or max_results == 0:
                max_results = len(source_data) if isinstance(
                    source_data, list) else 10

        # Pre-filter garbage content before sending to LLM
        filtered_sources = self._filter_garbage_content(source_data)

        source_count = len(source_data) if isinstance(source_data, list) else 1
        filtered_count = len(filtered_sources) if isinstance(
            filtered_sources, list) else 1

        self.logger.info(
            f"Curating {filtered_count} sources (filtered from {source_count})")

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "research_plan",
                f"⚖️ Evaluating and curating {filtered_count} sources (filtered from {source_count}) by credibility and relevance...",
                self.researcher.websocket,
            )

        response = ""
        try:
            response = await create_chat_completion(
                model=self.researcher.cfg.smart_llm_model,
                messages=[
                    {"role": "system", "content": f"{self.researcher.role}"},
                    {"role": "user", "content": self.researcher.prompt_family.curate_sources(
                        self.researcher.query, filtered_sources, max_results)},
                ],
                temperature=0.2,
                max_tokens=8000,
                llm_provider=self.researcher.cfg.smart_llm_provider,
                llm_kwargs=self.researcher.cfg.llm_kwargs,
                cost_callback=self.researcher.add_costs,
            )

            curated_sources = json.loads(response)
            curated_count = len(curated_sources) if isinstance(
                curated_sources, list) else 1
            self.logger.info(f"Curator finalized: {curated_count} sources")

            if self.researcher.verbose:
                await stream_output(
                    "logs",
                    "research_plan",
                    f"🏅 Verified and ranked top {curated_count} most reliable sources",
                    self.researcher.websocket,
                )

            return curated_sources

        except Exception as e:
            self.logger.error(
                f"Error in curate_sources: {str(e)}\nLLM Response: {response}")
            if self.researcher.verbose:
                await stream_output(
                    "logs",
                    "research_plan",
                    f"🚫 Source verification failed: {str(e)}",
                    self.researcher.websocket,
                )
            return filtered_sources  # Return filtered sources as fallback

    def _filter_garbage_content(self, source_data) -> List:
        """
        Filter out common garbage content patterns:
        - Error pages (404, 403, Access Denied)
        - Installation guides
        - Login/registration pages
        - Cookie consent pages
        - Empty or very short content

        Args:
            source_data: Can be a list of source documents or a string

        Returns:
            List of filtered source documents
        """
        import logging
        logger = logging.getLogger(__name__)

        # Handle string data - return as-is (already processed by compressor)
        if isinstance(source_data, str):
            logger.info(
                f"String context passed to filter - returning as-is ({len(source_data)} chars)")
            return source_data

        # Handle non-list data
        if not isinstance(source_data, list):
            logger.warning(f"Unexpected source_data type: {type(source_data)}")
            return []

        garbage_patterns = [
            # Error patterns
            "access denied", "403 forbidden", "404 not found", "page not found",
            "permission denied", "unauthorized", "error 404", "error 403",
            "this page doesn't exist", "page cannot be found",

            # Installation/setup patterns (case-insensitive)
            "windows 11 installation", "windows 10 installation", "how to install",
            "installation guide", "installation instructions", "setup wizard",
            "system requirements", "installation steps",

            # Login/registration patterns
            "sign in", "log in", "create account", "register now",
            "forgot password", "reset password", "login required",

            # Cookie/privacy patterns
            "cookie consent", "accept cookies", "privacy policy",
            "terms of service", "terms and conditions",

            # Generic error messages
            "something went wrong", "an error occurred", "please try again",
            "service unavailable", "temporarily unavailable"
        ]

        filtered_sources = []
        too_short_count = 0
        garbage_pattern_count = 0

        for source in source_data:
            # Get content for checking (try different possible keys)
            content = ""
            if isinstance(source, dict):
                # Try all common content keys
                content = (source.get("raw_content") or
                           source.get("content") or
                           source.get("body") or
                           source.get("text") or
                           source.get("page_content") or
                           "")
            elif hasattr(source, 'page_content'):
                # LangChain Document object
                content = source.page_content or ""
            elif isinstance(source, str):
                # Raw string
                content = source

            # Convert to lowercase for case-insensitive matching
            content_lower = content.lower() if content else ""

            # Skip if content is too short (likely error page or empty)
            if len(content.strip()) < 100:
                too_short_count += 1
                logger.debug(
                    f"Filtered source (too short): {len(content)} chars")
                continue

            # Check for garbage patterns
            is_garbage = False
            for pattern in garbage_patterns:
                if pattern.lower() in content_lower:
                    is_garbage = True
                    garbage_pattern_count += 1
                    logger.debug(
                        f"Filtered source (garbage pattern '{pattern}')")
                    break

            # Only include if not garbage
            if not is_garbage:
                filtered_sources.append(source)

        # Log filtering statistics
        logger.info(f"Content filtering: {len(source_data)} total → {len(filtered_sources)} kept "
                    f"({too_short_count} too short, {garbage_pattern_count} garbage patterns)")

        if len(filtered_sources) == 0 and len(source_data) > 0:
            logger.warning(f"⚠️ ALL {len(source_data)} sources were filtered out! "
                           f"Check content key names. Sample source keys: {list(source_data[0].keys()) if source_data and isinstance(source_data[0], dict) else 'N/A'}")

        return filtered_sources
