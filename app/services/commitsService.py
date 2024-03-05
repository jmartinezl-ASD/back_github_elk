from fastapi import HTTPException
from app.services.repositoryService import repositorios
import requests

## USUARIO COMMITS ##
def obtener_commits(usuario, repositorio, token=None): # mostrar los commits del usuario en el repositorio asociado 
    url = f"https://api.github.com/repos/{usuario}/{repositorio}/commits"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"} if token else {"Accept": "application/vnd.github.v3+json"}
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
# NO FUNCIONA O EXPLICAR () 
def obtener_commits_repositorio(nombre_repositorio, token): 
    url = f"https://api.github.com/repos/{nombre_repositorio}/commits"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
   
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        return commits
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los commits del repositorio {nombre_repositorio}: {str(e)}")

## COMMITS DEL USUARIO ##
def contar_commits_usuario(usuario, token):
    repositorios_usuario = repositorios(token)
    if repositorios_usuario is None:
        return None
 
    total_commits = 0
    for repo in repositorios_usuario:
        commits = obtener_commits_repositorio(repo["full_name"], token)
        if commits is not None:
            commits_usuario = [commit for commit in commits if commit["author"] is not None and commit["author"]["login"] == usuario]
            total_commits += len(commits_usuario)
 
    return total_commits