from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.settings import settings

def get_api_key(x_api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False))):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Задан неверный ключ")
    return x_api_key
