from fastapi import FastAPI
from src.adapters.web.fastapi.router import api_router

app = FastAPI(
    title = 'Video Background Remover',
    version = '1',
    description= 'API that removes background from videos'
)

app.include_router(api_router)