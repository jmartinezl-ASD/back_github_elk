from fastapi import APIRouter,HTTPException
from app.services.commitsService import service_commits
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
router = APIRouter(prefix="/Commits", tags=["Commit"])

###### COMMITS ######   
## RUTA COMMITS USUARIO ##
@router.get("/Informacion")
async def obtener_commits_repositorio(usuario: str, repositorio: str):
    if not TOKEN:
        raise HTTPException(status_code=500, detail="Token de acceso a GitHub no proporcionado")
    try:
        commits = service_commits(usuario, repositorio, TOKEN)
        return commits
    except HTTPException as e:
        raise e
    
