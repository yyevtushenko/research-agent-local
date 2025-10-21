from gpt_researcher.utils.workers import WorkerPool
from typing import Optional
from datetime import datetime, timedelta
import logging

from ..actions.utils import stream_output
from ..actions.web_scraping import scrape_urls
from ..scraper.utils import get_image_hash

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages context for the researcher agent."""

    def __init__(self, researcher):
        self.researcher = researcher
        self.worker_pool = WorkerPool(researcher.cfg.max_scraper_workers)

    async def browse_urls(self, urls: list[str]) -> list[dict]:
        """
        Scrape content from a list of URLs.
        Checks Qdrant cache first for URLs scraped within 72 hours.

        Args:
            urls (list[str]): list of URLs to scrape.

        Returns:
            list[dict]: list of scraped content results.
        """
        from datetime import datetime, timedelta

        # URLs are already filtered by researcher._get_new_urls() which checks Qdrant cache
        # No need for redundant cache check here - just scrape what we're given
        urls_to_scrape = urls
        cached_content = []  # Empty since URLs are pre-filtered

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "scraping_urls",
                f"🌐 Scraping content from {len(urls_to_scrape)} URLs...",
                self.researcher.websocket,
            )

        # Scrape only the URLs not in cache
        scraped_content = []
        images = []
        if urls_to_scrape:
            scraped_content, images = await scrape_urls(
                urls_to_scrape, self.researcher.cfg, self.worker_pool
            )

        # Combine cached and newly scraped content
        all_content = cached_content + scraped_content

        self.researcher.add_research_sources(all_content)
        new_images = self.select_top_images(images, k=4)  # Select top 4 images
        self.researcher.add_research_images(new_images)

        if self.researcher.verbose:
            # Report scraped count (cached URLs were already filtered upstream in researcher._get_new_urls)
            total_cache_hits = getattr(self.researcher, 'cache_hits', 0)
            await stream_output(
                "logs",
                "scraping_content",
                f"📄 Total content: {total_cache_hits} cached (filtered) + {len(scraped_content)} scraped = {total_cache_hits + len(scraped_content)} total URLs processed",
                self.researcher.websocket,
            )
            await stream_output(
                "logs",
                "scraping_images",
                f"🖼️ Selected {len(new_images)} new images from {len(images)} total images",
                self.researcher.websocket,
                True,
                new_images,
            )
            await stream_output(
                "logs",
                "scraping_complete",
                f"🌐 Scraping complete",
                self.researcher.websocket,
            )

        # Store newly scraped content in Qdrant for future caching
        import logging
        logger = logging.getLogger(__name__)

        # CRITICAL DEBUG: Log scraped_content IMMEDIATELY before caching check
        logger.warning(
            f"🔴 [PRE-CACHE] scraped_content type={type(scraped_content)}, len={len(scraped_content) if scraped_content else 'None'}")
        if scraped_content and len(scraped_content) > 0:
            logger.warning(
                f"🔴 [PRE-CACHE] First 3 items keys: {[list(item.keys()) for item in scraped_content[:3]]}")
            logger.warning(
                f"🔴 [PRE-CACHE] First item raw_content length: {len(scraped_content[0].get('raw_content', '')) if scraped_content else 0}")
        else:
            logger.warning(f"🔴 [PRE-CACHE] scraped_content is EMPTY or None!")

        # Use explicit lengths and types in the logs because INFO may be suppressed
        scraped_len = len(
            scraped_content) if scraped_content is not None else 0
        has_qdrant_attr = hasattr(self.researcher, 'qdrant_store')
        qdrant_exists = bool(getattr(self.researcher, 'qdrant_store', None))
        urls_to_scrape_len = None
        try:
            # urls_to_scrape is defined in the outer scope of this function
            # type: ignore[name-defined]
            urls_to_scrape_len = len(urls_to_scrape)
        except Exception:
            urls_to_scrape_len = 'unknown'

        # Emit at WARNING so it appears in default logging outputs; include counts so it's diagnostic
        if scraped_len > 0 and has_qdrant_attr and qdrant_exists:
            logger.warning(
                f"✅ Conditions met for caching: caching {scraped_len} scraped items (urls_to_scrape={urls_to_scrape_len})")
            await self._cache_scraped_content(scraped_content)
        else:
            logger.warning(
                "⚠️ Caching skipped: "
                f"scraped_len={scraped_len}, has_qdrant_attr={has_qdrant_attr}, "
                f"qdrant_exists={qdrant_exists}, urls_to_scrape={urls_to_scrape_len}"
            )

        return all_content

    async def _cache_scraped_content(self, scraped_content: list[dict]) -> None:
        """
        Store scraped content in Qdrant for future caching.

        Args:
            scraped_content: List of scraped content dicts
        """
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)

        if not scraped_content:
            logger.debug("No scraped content to cache")
            return

        # Filter out content with no raw_content or minimal content
        # Use threshold of 30 chars to capture even short snippets (consistent with scraper lowered 50-char threshold)
        valid_items = [
            item for item in scraped_content
            if item.get('url') and item.get('raw_content') and len(item.get('raw_content', '')) > 30
        ]

        if not valid_items:
            logger.debug(
                f"No valid content to cache from {len(scraped_content)} items")
            return

        logger.info(f"💾 Caching {len(valid_items)} scraped pages to Qdrant...")

        try:
            for item in valid_items:
                url = item.get('url', '')
                content = item.get('raw_content', '')
                title = item.get('title', '')

                # Store with metadata including URL and timestamp
                metadata = {
                    'url': url,
                    'title': title,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'scraped_content'
                }

                # Store in Qdrant
                result = await self.researcher.store_in_qdrant(
                    texts=[content],
                    metadata=[metadata]
                )

                if not result:
                    logger.warning(f"⚠️ Failed to cache: {url}")

        except Exception as e:
            logger.error(
                f"❌ Error caching content: {type(e).__name__}: {e}", exc_info=True)
            # Don't fail the research if caching fails
            if self.researcher.verbose:
                await stream_output(
                    "logs",
                    "cache_error",
                    f"⚠️ Failed to cache content: {str(e)}",
                    self.researcher.websocket,
                )

    def select_top_images(self, images: list[dict], k: int = 2) -> list[str]:
        """
        Select most relevant images and remove duplicates based on image content.

        Args:
            images (list[dict]): list of image dictionaries with 'url' and 'score' keys.
            k (int): Number of top images to select if no high-score images are found.

        Returns:
            list[str]: list of selected image URLs.
        """
        unique_images = []
        seen_hashes = set()
        current_research_images = self.researcher.get_research_images()

        # Process images in descending order of their scores
        for img in sorted(images, key=lambda im: im["score"], reverse=True):
            img_hash = get_image_hash(img['url'])
            if (
                img_hash
                and img_hash not in seen_hashes
                and img['url'] not in current_research_images
            ):
                seen_hashes.add(img_hash)
                unique_images.append(img["url"])

                if len(unique_images) == k:
                    break

        return unique_images
