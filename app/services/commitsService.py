from fastapi import HTTPException
from app.services.repositoryService import service_repositorios
import requests
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_API_URL = os.getenv('GITHUB_API_URL')
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

## USUARIO COMMITS ##
def service_commits(usuario, repositorio,TOKEN):
    url = f"{GITHUB_API_URL}/repos/{usuario}/{repositorio}/commits"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"} if TOKEN else {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        detail = f"Error al obtener commits: {e.response.content.decode()}"
        raise HTTPException(status_code=status_code, detail=detail)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al conectarse a la API de GitHub: {str(e)}")
    
## REPOSITORIO COMMITS ##
def service_commits_repositorio(nombre_repositorio):
    url = f"{GITHUB_API_URL}/repos/{nombre_repositorio}/commits"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
   
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        return len(commits)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los commits del repositorio {nombre_repositorio}: {str(e)}")

