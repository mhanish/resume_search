# Router instance
from fastapi.routing import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from search import ResumeParser, search_query, expand_query

router = APIRouter()


class Query(BaseModel):
    query: str = Field(..., max_length=5000)


@router.get(
    "/ping",
    tags=["Ping"],
    description="""***Endpoint to ping and verify your API keys***""",
)
async def ping(request: Request):

    return {
        "message": "Ping successful",
    }


@router.post(
    "/search",
    tags=["Search"],
    description="***Searches through the resumes based on input query***",
)
async def search(
    request: Query,
):

    try:
        new_query = expand_query(request.query)
        resp = search_query(query=new_query)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
