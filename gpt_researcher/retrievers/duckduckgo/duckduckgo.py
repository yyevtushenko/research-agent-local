from itertools import islice
import logging
from ..utils import check_pkg, truncate_query

logger = logging.getLogger(__name__)


class Duckduckgo:
    """
    Duckduckgo API Retriever
    """

    def __init__(self, query, query_domains=None):
        check_pkg('ddgs')
        from ddgs import DDGS
        self.ddg = DDGS()
        self.query = truncate_query(query)
        self.query_domains = query_domains or None

    def search(self, max_results=5, excluded_domains=None):
        """
        Performs the search with optional domain filtering.

        Note: DuckDuckGo does NOT support wildcard site: operators like site:*.de
        Instead, if query_domains are provided, we run separate queries for each domain
        and combine results (DuckDuckGo-compatible approach).

        :param max_results: Maximum number of results to return
        :param excluded_domains: List of domain names to filter out from results
        :return: List of search results
        """
        if excluded_domains is None:
            excluded_domains = []

        logger.info(
            f"DuckDuckGo search with {len(excluded_domains)} excluded domains: {excluded_domains[:3]}...")

        def filter_excluded(results):
            """Filter out URLs containing excluded domains"""
            filtered = []
            logger.warning(
                f"🔍 DuckDuckGo returned {len(results)} raw results, filtering now...")
            for result in results:
                url = result.get('href', '').lower()
                # Check if URL contains any excluded domain
                is_excluded = any(
                    domain.lower() in url for domain in excluded_domains)
                if not is_excluded:
                    filtered.append(result)
                else:
                    logger.warning(
                        f"🚫 BLOCKED EXCLUDED DOMAIN from DuckDuckGo: {url}")
            logger.warning(
                f"✅ After filtering: {len(filtered)} results remain")
            return filtered

        try:
            # If no query_domains specified, run a single search
            if not self.query_domains:
                try:
                    search_response = self.ddg.text(
                        self.query, region='wt-wt', max_results=max_results * 2)  # Get more to compensate for filtering
                    filtered_results = filter_excluded(search_response)
                    return filtered_results[:max_results]
                except Exception as ddg_error:
                    # Ignore Wikipedia DNS errors - they're harmless
                    if 'wt.wikipedia.org' in str(ddg_error) or 'wikipedia' in str(ddg_error).lower():
                        logger.debug(
                            f"Wikipedia engine failed (expected): {ddg_error}")
                        return []
                    raise  # Re-raise non-Wikipedia errors

            # If query_domains are specified, run separate searches for each domain
            # and combine results (DuckDuckGo doesn't support site:*.de wildcards)
            all_results = []
            # Get more for filtering
            results_per_domain = max(
                1, (max_results * 2) // len(self.query_domains))

            for domain in self.query_domains:
                # DuckDuckGo only supports exact domain in site: operator
                # No wildcards like site:*.de - use exact domain only
                domain_query = f"{self.query} site:{domain}"
                try:
                    domain_results = self.ddg.text(
                        domain_query, region='wt-wt', max_results=results_per_domain)
                    filtered_domain_results = filter_excluded(domain_results)
                    all_results.extend(filtered_domain_results)
                except Exception as e:
                    logger.error(f"Error searching domain {domain}: {e}")
                    continue

            # Return up to max_results combined from all domains
            return list(islice(all_results, max_results))

        except Exception as e:
            logger.error(
                f"Error: {e}. Failed fetching sources. Resulting in empty response.")
            return []
