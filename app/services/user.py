from fastapi import HTTPException
from app.schema.user import userSchema
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import requests
import os

load_dotenv()
GITHUB_API_URL = os.getenv('GITHUB_API_URL')
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

elastic_search_url = os.getenv('ELASTIC_SEARCH_URL', 'http://localhost:9200')
es = Elasticsearch(elastic_search_url)

async def miembros_organización_servicio(): 
    miembros_data = []
    url = f"{GITHUB_API_URL}/orgs/{ORG}/members"

    headers = {"Authorization": f"token {TOKEN}"}
    params = {"per_page": 100, "page": 1} 
        
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
        
    data = response.json()

    for miembro in data:
        info_miembro = userSchema(**miembro)  
        miembros_data.append(info_miembro)
    
    return miembros_data


# USUARIOS MÁS ACTIVOS

async def miembros_activos_servicio():
    headers = {"Authorization": f"token {TOKEN}"}
    url = f"{GITHUB_API_URL}/orgs/{ORG}/repos"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al traer los repositorios de la organización")

    repos = response.json()
    contribuciones_info = {}

    for repo in repos:
        repo_nombre = repo['name']
        url = f"{GITHUB_API_URL}/repos/{ORG}/{repo_nombre}/contributors"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            colaboradores = response.json()
            for colaborador in colaboradores:
                login = colaborador['login']
                colaboraciones = colaborador['contributions']
                if login in contribuciones_info:
                    contribuciones_info[login]['total_contributions'] += colaboraciones
                    contribuciones_info[login]['repositories'][repo_nombre] = colaboraciones
                else:
                    contribuciones_info[login] = {
                        'total_contributions': colaboraciones,
                        'repositories': {repo_nombre: colaboraciones}
                    }

    colaboradores_clasificados = sorted(contribuciones_info.items(), key=lambda x: x[1]['total_contributions'], reverse=True)

    colaboradores_activos_data = []

    for login, info in colaboradores_clasificados:
        data = {
            "username": login, 
            "Total contribuciones": info['total_contributions'],
            "Repositorios": info['repositories']
        }
        colaboradores_activos_data.append(data)

    return colaboradores_activos_data

# INDEXACIÓN EN ELASTIC EN PROCESO

async def index_members_GrupoASD(all_members_data):
    for member_data in all_members_data:
        es.index(index="members_grupo-asd", id=member_data.id, document=member_data.dict())