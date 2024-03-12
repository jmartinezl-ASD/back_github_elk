import requests
from datetime import datetime, timedelta
from app.services.repositoryService import services_repositorios_org
from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_API_URL = os.getenv('GITHUB_API_URL')
TOKEN = os.getenv('TOKEN')
ORG = os.getenv('ORG')

def obtener_ramas(repo):
    url = f"{GITHUB_API_URL}/repos/{ORG}/{repo}/branches"
    headers = {"Authorization": f"token {TOKEN}"}
    ramas = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ramas_data = response.json()
        for rama in ramas_data:
            ramas.append(rama['name'])
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener las ramas: {e}")
    return ramas

def contar_commits_recientes(repo, rama, desde):
    url_base = f"{GITHUB_API_URL}/repos/{ORG}/{repo}/commits?sha={rama}"
    headers = {"Authorization": f"token {TOKEN}"}
    commits_recientes = 0

    url = f"{url_base}&since={desde}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits_recientes = len(response.json())

        while 'next' in response.links:
            response = requests.get(response.links['next']['url'], headers=headers)
            response.raise_for_status()
            commits_recientes += len(response.json())
            
    except requests.exceptions.RequestException as e:
        print(f"Error al contar los commits recientes para la rama {rama}: {e}")

    return commits_recientes

def contar_commits(repo, rama):
    total_commits = 0
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{repo}/commits?sha={rama}&page={page}&per_page=100"
        headers = {"Authorization": f"token {TOKEN}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                commits = response.json()
                commit_count = len(commits)
                total_commits += commit_count
                if commit_count < 100:
                    break
                page += 1
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error al contar los commits para la rama {rama}: {e}")
            break
    return total_commits

def obtener_commits(repo, desde=None):
    url_base = f"{GITHUB_API_URL}/repos/{ORG}/{repo}/commits"
    commits_totales = 0
    commits_recientes = 0
    headers = {"Authorization": f"token {TOKEN}"}

    try:
        url = url_base + "?per_page=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if 'last' in response.links:
            last_page = response.links['last']['url']
            last_page_num = int(last_page.split('=')[-1])
            commits_totales = last_page_num * 1
        else:
            commits_totales = len(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el total de commits: {e}")

    if desde:
        page = 1
        while True:
            url = f"{url_base}?since={desde}&page={page}&per_page=100"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                commits = response.json()
                if not commits:
                    break
                commits_recientes += len(commits)
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener los commits recientes: {e}")
                break

    return commits_totales, commits_recientes

def service_repositorios_actividad():
    repositorios = services_repositorios_org()
    if not repositorios:
        return {"error": "No se encontraron repositorios para la organización"}

    actividad_repos = []
    for repo in repositorios:
        nombre_repo = repo['name']
        ramas = obtener_ramas(nombre_repo)
        rama_con_mas_commits = ""
        rama_con_mas_commits_semana = ""
        max_commits = 0
        max_commits_semana = 0
        commits_ultima_semana = 0

        desde = (datetime.now() - timedelta(days=20)).isoformat()
        
        for rama in ramas:
            total_commits = contar_commits(nombre_repo, rama)
            if total_commits > max_commits:
                max_commits = total_commits
                rama_con_mas_commits = rama
            
            commits_recientes = contar_commits_recientes(nombre_repo, rama, desde)
            if commits_recientes > max_commits_semana:
                max_commits_semana = commits_recientes
                rama_con_mas_commits_semana = rama
                commits_ultima_semana = commits_recientes

        actividad_repos.append({
            "nombre": nombre_repo,
            "rama_con_mas_commits": rama_con_mas_commits,
            "rama_con_mas_commits_semana": rama_con_mas_commits_semana,
            "commits_ultima_semana": commits_ultima_semana
        })
    actividad_repos_ordenada = sorted(actividad_repos, key=lambda x: x["commits_ultima_semana"], reverse=True)

    return actividad_repos_ordenada
