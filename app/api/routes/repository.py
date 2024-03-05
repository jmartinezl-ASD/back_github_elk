from fastapi import APIRouter, HTTPException
from app.services.repositoryService import repositorios

router = APIRouter(prefix="/Repository", tags=["Repository"])

@router.get("/repositorios")
async def obtener_repositorios_api(token: str = None):
    lista_repositorios = repositorios(token)
    if lista_repositorios:
        return {"Repositorios": [repo["name"] for repo in lista_repositorios]}
    else:
        raise HTTPException(status_code=404, detail="No se encontraron repositorios para el usuario especificado")   
