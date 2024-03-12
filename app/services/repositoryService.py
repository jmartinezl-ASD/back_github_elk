import requests
import datetime
from fastapi import HTTPException
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_API_URL = os.getenv('GITHUB_API_URL')
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

def service_repositorios():
    url = f"{GITHUB_API_URL}/user/repos"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
   
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        repositorios = response.json()
        return repositorios
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la lista de repositorios: {str(e)}")
    
def services_repositorios_org():
    url = f"https://api.github.com/orgs/{ORG}/repos"
    headers = {"Authorization": f"token {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        repositorios = response.json()
        return repositorios
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la lista de repositorios: {str(e)}")
    
def service_ramas_repositorio(usuario: str, repositorio: str):
    if not TOKEN:
        raise HTTPException(status_code=401, detail="Token de acceso no proporcionado o inválido")
    
    url = f"https://api.github.com/repos/{usuario}/{repositorio}/branches"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error al obtener las ramas de GitHub")

    branches = response.json()
    branch_names = [branch["name"] for branch in branches]
    return branch_names

# GET - pulls
def service_Pulls_repos():
    repositorios = services_repositorios_org()
    if repositorios:
        repos_dict = {}
        for repo in repositorios:
            nombre_repo = repo["name"]
            page = 1
            while True:
                url = f"https://api.github.com/repos/{ORG}/{nombre_repo}/pulls?state=all&per_page=100&page={page}"
                headers = {
                    "Authorization": f"token {TOKEN}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    pulls = response.json()
                    contador_pulls = len(pulls)
                    num_pulls_abiertos = len([pull for pull in pulls if pull["state"] == "open"])
                    num_pulls_cerrados = len([pull for pull in pulls if pull["state"] == "closed"])

                    if nombre_repo in repos_dict:
                        repos_dict[nombre_repo]["numero_pulls"] += contador_pulls
                        repos_dict[nombre_repo]["numero_pulls_abiertos"] += num_pulls_abiertos
                        repos_dict[nombre_repo]["numero_pulls_cerrados"] += num_pulls_cerrados
                    else:
                        repos_dict[nombre_repo] = {
                            "nombre_repo": nombre_repo,
                            "numero_pulls": contador_pulls,
                            "numero_pulls_abiertos": num_pulls_abiertos,
                            "numero_pulls_cerrados": num_pulls_cerrados
                        }
                    page += 1 
                    if contador_pulls != 100:
                        break  
                else:
                    continue  
        return list(repos_dict.values())
    else:
        return {"error": "No se encontraron repositorios"}

#GET - branches
def services_Branches_repos():
    repositorios = services_repositorios_org()
    if repositorios:
        lista_ramas = []
        for repo in repositorios:
            nombre_repo = repo["name"]
            url = f"https://api.github.com/repos/{ORG}/{nombre_repo}/branches"
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                ramas = response.json()
                num_ramas = len(ramas)
                branch_names = [branch["name"] for branch in ramas]  # Extract branch names

                lista_ramas.append({"repositorio": nombre_repo, "numero_ramas": num_ramas, "ramas": branch_names})
            else:
                lista_ramas.append({"repositorio": nombre_repo, "error": f"Error en la consulta: {response.text}"})

        return lista_ramas

# GIT - lenguajes    
def service_Lenguajes_repos():
    repositorios = services_repositorios_org()
    if repositorios:
        lista_lenguajes = []
        for repo in repositorios:
            nombre_repo = repo["name"]
            url_branches = f"https://api.github.com/repos/{ORG}/{nombre_repo}/branches"
            url_languages = f"https://api.github.com/repos/{ORG}/{nombre_repo}/languages"
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            response_branches = requests.get(url_branches, headers=headers)
            response_languages = requests.get(url_languages, headers=headers)

            if response_branches.status_code == 200 and response_languages.status_code == 200:
                branches = response_branches.json()
                branch_names = [branch["name"] for branch in branches]  # Extract branch names

                languages = response_languages.json()
                total_languages = sum(languages.values())

                porcentajes = {lenguaje: round((cantidad / total_languages) * 100, 0) for lenguaje, cantidad in languages.items()}

                # lista_lenguajes.append({"repositorio": nombre_repo, "ramas": branch_names, "lenguajes": porcentajes})
                lista_lenguajes.append({"repositorio": nombre_repo, "lenguajes": porcentajes})
            else:
                lista_lenguajes.append({"repositorio": nombre_repo, "error": f"Error en la consulta: {response_branches.text} | {response_languages.text}"})

        return lista_lenguajes
    else:
        return {"error": "No se encontraron repositorios"}

#GIT - issues
def service_Issues_repos():
    repositorios = services_repositorios_org()
    if repositorios:
        
        lista_issues = []
        
        for repo in repositorios:
            nombre_repo = repo["name"]
            url = f"https://api.github.com/repos/{ORG}/{nombre_repo}/issues?state=all"
            headers = {
                "Authorization": f"token {TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                
                issues = response.json()
                
                num_issues_abiertos = len([ussue for ussue in issues if ussue["state"] == "open"])
                num_issues_cerrados = len([ussue for ussue in issues if ussue["state"] == "closed"])
                resultados = []

                for issue in issues:
                    if issue["closed_at"] != None and issue["created_at"] != None:
                        
                        creado_txt = str(issue["created_at"])[:10]
                        cerrado_txt = str(issue["closed_at"])[:10]

                        creado = datetime.datetime.strptime(creado_txt, "%Y-%m-%d").date()
                        cerrado = datetime.datetime.strptime(cerrado_txt, "%Y-%m-%d").date()
                        
                        tiempo_solucion = (cerrado - creado).days
                        
                        resultados.append({"id": issue["id"], "titulo": issue["title"], "fecha_creacion": creado, "fecha_cierre": cerrado, "solucionado_dias": tiempo_solucion})
                  
                lista_issues.append({"repositorio": nombre_repo, "issues_abiertos": num_issues_abiertos, "issues_cerrados": num_issues_cerrados, "info_issues_cerrados": resultados})            
            else:
                lista_issues.append({"repositorio": nombre_repo, "error": f"Error en la consulta: {response.text}"})
             
        return lista_issues
    else: 
        return Exception(status_code=response.status_code, detail=response.text), print(lista_issues.error), print(lista_issues)
