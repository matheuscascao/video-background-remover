import uvicorn
from src.adapters.web.fastapi.index import app

if __name__ == '__main__':    
    uvicorn.run(
        app=app,
        host="127.128.0.1",
        port=8080,
        log_level="info",
        reload=True,
    )