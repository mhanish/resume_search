from fastapi import FastAPI
from router import router

app = FastAPI(
    title="Semantic Search API",
    version="0.3.0",
    redoc_url="/docs",
    docs_url="/swagger",
    servers=[
        {"url": "http://localhost:8000", "description": "Development"},
    ],
)

app.include_router(router=router)
