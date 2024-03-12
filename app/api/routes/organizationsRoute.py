from fastapi import APIRouter, HTTPException
from app.services.organizationService import lista_incidencias_org
from app.services.commitsService import service_commits_repositorio
from dotenv import load_dotenv
import os
import requests

load_dotenv()

TOKEN = os.getenv("TOKEN")
ORG = os.getenv("ORG")

router = APIRouter(prefix="/Organizacion", tags=["Organizacion"])

@router.get("/incidencias_repositorio_org")
async def incidencias_repositorio_org():
    
    #Almacenamos el resultado de la constulta en una variable
    repos_org = await lista_incidencias_org()

    