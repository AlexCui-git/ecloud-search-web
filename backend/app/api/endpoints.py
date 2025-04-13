from fastapi import APIRouter, HTTPException
from app.core.models import SearchQuery, SearchResponse
from app.core.scraper.search_automation import ECloudSearcher
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
searcher = None

def get_searcher():
    global searcher
    if searcher is None:
        logger.info("Initializing new ECloudSearcher instance")
        searcher = ECloudSearcher()
    return searcher

@router.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery):
    try:
        result = await get_searcher().get_best_answer(query.query)
        return result
    except ModuleNotFoundError as e:
        logger.error(f"Missing module: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: Missing required module"
        )
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))