from fastapi import APIRouter,HTTPException
from app.services.commitsService import obtener_commits,contar_commits_usuario

router = APIRouter(prefix="/Commits", tags=["Commit"])

###### COMMITS ######   
## RUTA COMMITS USUARIO ##
@router.get("/commits/{usuario}/{repositorio}")
async def obtener_commits_api(usuario: str, repositorio: str, token: str = None):
    try:
        commits = obtener_commits(usuario, repositorio, token)
        return commits
    except HTTPException as e:
        raise e

## RUTA CONTEO COMMITS ##
@router.get("/commits/usuario")
async def obtener_total_commits_usuario(usuario: str, token: str):
    total_commits_usuario = contar_commits_usuario(usuario, token)
    return {"total_commits_usuario": total_commits_usuario}
    


    
