from fastapi import APIRouter, HTTPException
from app.services.repositoryService import service_repositorios,services_repositorios_org,service_ramas_repositorio, service_Pulls_repos, services_Branches_repos, service_Lenguajes_repos, service_Issues_repos
from app.services.repositoryService import service_repositorios,services_repositorios_org,service_ramas_repositorio
from app.services.repositoryOrgService import service_repositorios_actividad
from dotenv import load_dotenv
import os
import requests

import json

load_dotenv()
TOKEN = os.getenv("TOKEN")
ORG = os.getenv("ORG")
GITHUB_API_URL = os.getenv("GITHUB_API_URL")

router = APIRouter(prefix="/Repository", tags=["Repository"])

@router.get("/usuario")
async def repositorios_usuario():
    lista_repositorios = service_repositorios()
    if lista_repositorios:
        return {"Repositorios": [repo["name"] for repo in lista_repositorios]}
    else:
        raise HTTPException(status_code=404, detail="No se encontraron repositorios para el usuario especificado") 
    
@router.get("/org")
async def repositorios_org():
    repositorios = services_repositorios_org()
    if repositorios:
        return {"repositorios": [repo["name"] for repo in repositorios]}
    else:
        raise HTTPException(status_code=404, detail="No se encontraron repositorios para la organización especificada")


@router.get("/ramas")
async def ramas_repositorio(usuario: str, repositorio: str):
    branches = service_ramas_repositorio(usuario, repositorio)
    return {"branches": branches}

@router.get("/mas-activo-org")
async def repositorios_actividad():
    actividad = service_repositorios_actividad()
    return {"Repositorios": actividad}

# GET - lista de errores por repositorios
@router.get("/issues_repos") 
async def Issues_repositorio():
    issues = service_Issues_repos()
    return {"incidencia": issues}

# GET - lista de lenguajes usados en los repositorios 
@router.get("/Lenguajes_repos") 
async def languages_repositorio():
    lenguajes = service_Lenguajes_repos()
    return {"lenguajes": lenguajes}

# GET - Contador de ramas de un repositorio
@router.get("/branches_repos") 
async def ramas_repositorio():
    branches = services_Branches_repos()
    return {"Ramas": branches}

# GET - Contador de pulls de un repositorio
@router.get("/Pulls_repos")
async def pulls_repositorio():
    pulls = service_Pulls_repos()
    return {"Pulls": pulls}