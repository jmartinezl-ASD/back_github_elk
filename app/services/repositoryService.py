import requests
from fastapi import HTTPException

def repositorios(token): # muestra repositorios relacionados al token
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
   
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Nos dara un HTTPException si hay un error en la respuesta
        repositorios = response.json()
        return repositorios
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la lista de repositorios: {str(e)}")