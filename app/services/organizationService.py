from elasticsearch import Elasticsearch
from fastapi import HTTPException
from dotenv import load_dotenv
import requests
import os

load_dotenv()
elastic_search_url = os.getenv('ELASTIC_SEARCH_URL', 'http://localhost:9200')
es = Elasticsearch(elastic_search_url)
GITHUB_API_URL = os.getenv('GITHUB_API_URL')
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

async def lista_repositorios_org():
    url = f"{GITHUB_API_URL}/orgs/{ORG}/repos"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repos_org = response.json()
        
        # Calidad de código
        for repo in repos_org:
            repo_nombre = repo["name"]
            repo_open_issues = repo["open_issues_count"]
            
            # Porcentaje de problemas solucionados
            porcentaje_issues_abiertos = (repo_open_issues * 100) / repos_org
        
            url = f"{GITHUB_API_URL}/repos/{ORG}/{repo_nombre}/issues"
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            if response.status_code == 200:
                issues_data = response.data()
                
    

    
    else:
        return HTTPException(status_code=response.status_code, detail=response.text)

async def lista_incidencias_org():
    url = f"{GITHUB_API_URL}/orgs/{ORG}/issues"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  
    else:
        return HTTPException(status_code=response.status_code, detail=response.text)

async def lista_equipos_org():
    url = f"{GITHUB_API_URL}/orgs/{ORG}/teams"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  
    elif response.status_code == 403:
        return f"Acceder aqui esta prohibido."
    else:
        return HTTPException(status_code=response.status_code, detail=response.text)
    
async def lista_miembros_org():
    url = f"{GITHUB_API_URL}/orgs/{ORG}/members"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }   
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  
    elif response.status_code == 403:
        return f"Acceder aqui esta prohibido."
    
    elif response.status_code == 404:
        return f"No se encontro nada."
    
    elif response.status_code == 410:
        return f"La organización tiene deshsbilitada esta opción." 
    
    else: #En un caso contrario a los espeficicados anterior.
        return HTTPException(status_code=response.status_code, detail=response.text)
    
    
# GET - CONFIRMAR MIEMBROS - Confirmar si un usuario es parte de la organización
async def confirmar_miembros_org(USU = str):
    
    # Preparación de la consulta con parametros.
    url = f"{GITHUB_API_URL}/orgs/{ORG}/members/{USU}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    response = requests.get(url, headers=headers)

    # Flujo de condicionales segun el estado de la respuesta de GitHub
    if response.status_code == 204: # En caso de que la consulta no sea exitosa.
        return f"El usuario {USU} si es miembro de la organización."  
        
    elif response.status_code == 403:
        return f"Acceder aqui esta prohibido."
    
    elif response.status_code == 404:
        return f"El usuario {USU} no es miembro de la organización."
    
    elif response.status_code == 410:
        return f"La organización tiene deshsbilitada esta opción." 
    
    else: #En un caso contrario a los espeficicados anterior.
        return HTTPException(status_code=response.status_code, detail=response.text)
    
    
    # # Almacenamos la respuesra del servidor en una variable.
    # response_data = response.json()

    # # Limpieza y estructura de datos provenientes de la respuesta.
    # data = {}

    # # Enviamos la informacion de la variable data como un index a Elastic.
    # try:
    #     es.index(index="github_users", id=data["id"], document=data)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    # return data
    
    # INDEXACIÓN EN ELASTIC EN PROCESO

async def index_members_GrupoASD(all_members_data):
    for member_data in all_members_data:
        es.index(index="members_grupo-asd", id=member_data.id, document=member_data.dict())