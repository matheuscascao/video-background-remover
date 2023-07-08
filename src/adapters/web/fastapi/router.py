from src.adapters.web.fastapi.controller.background_remover import background_remover
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(background_remover, prefix='/api', tags=['background_remover'])
