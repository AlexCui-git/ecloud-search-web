from app.core.scraper.search_automation import ECloudSearcher
import logging

logger = logging.getLogger(__name__)
_searcher = None

def get_searcher() -> ECloudSearcher:
    global _searcher
    if _searcher is None:
        logger.info("Initializing new ECloudSearcher instance")
        _searcher = ECloudSearcher()
    return _searcher