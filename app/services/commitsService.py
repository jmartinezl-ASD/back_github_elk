from fastapi import HTTPException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from dotenv import load_dotenv
from datetime import datetime
from config import config
import requests
import logging
import os

load_dotenv()

ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME").strip()
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD").strip()

es = Elasticsearch(
    [ELASTIC_SEARCH_URL], http_auth=(ELASTICSEARCH_USERNAME, ELASTIC_PASSWORD)
)


async def commits_usuario_repo():
    repo_commits_count = []
    headers = {"Authorization": f"token {config['TOKEN']}"}
    repos_url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?per_page=100"
    page = 1
    while True:
        paginated_repos_url = f"{repos_url}&page={page}"
        repos_response = requests.get(paginated_repos_url, headers=headers)
        if repos_response.status_code != 200:
            raise HTTPException(
                status_code=repos_response.status_code,
                detail="Error al obtener los repositorios de la organización",
            )
        repos = repos_response.json()
        if not repos:
            break

        for repo in repos:
            repo_nombre = repo["name"]
            repo_id = repo["id"]
            contribs_page = 1
            while True:
                contribs_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/contributors?per_page=100&page={contribs_page}"
                contribs_response = requests.get(contribs_url, headers=headers)
                if contribs_response.status_code != 200:
                    break
                colaboradores = contribs_response.json()
                if not colaboradores:
                    break

                for colaborador in colaboradores:
                    login = colaborador["login"]
                    commits_page = 1
                    while True:
                        commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?author={login}&per_page=100&page={commits_page}"
                        commits_response = requests.get(commits_url, headers=headers)
                        if commits_response.status_code != 200:
                            break
                        commits = commits_response.json()
                        if not commits:
                            break

                        repo_commits_count.append(
                            {
                                "id_repositorio": repo_id,
                                "Repositorio": repo_nombre,
                                "usuario": login,
                                "commits": len(commits),
                            }
                        )
                        commits_page += 1
                contribs_page += 1
        page += 1

    return repo_commits_count


def commits_por_dia_func():
    headers = {"Authorization": f"token {config['TOKEN']}"}
    repos_url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?per_page=100"
    resultados = []
    page = 1
    while True:
        paginated_repos_url = f"{repos_url}&page={page}"
        repos_response = requests.get(paginated_repos_url, headers=headers)
        if repos_response.status_code != 200:
            raise HTTPException(
                status_code=repos_response.status_code,
                detail="Error al obtener los repositorios de la organización",
            )

        repos = repos_response.json()
        if not repos:
            break

        for repo in repos:
            repo_nombre = repo["name"]
            repo_id = repo["id"]
            commits_page = 1
            all_commit_dates = []
            while True:
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?per_page=100&page={commits_page}"
                commits_response = requests.get(commits_url, headers=headers)

                if commits_response.status_code != 200:
                    break

                repo_commits = commits_response.json()
                if not repo_commits:
                    break

                for commit in repo_commits:
                    commit_date = commit["commit"]["committer"]["date"].split("T")[0]
                    all_commit_dates.append(commit_date)

                commits_page += 1

            total_dias = len(set(all_commit_dates))
            total_commits = len(all_commit_dates)
            media_commits_por_dia = total_commits / total_dias if total_dias > 0 else 0
            commits_por_dia = {
                "Repositorio": repo_nombre,
                "id_repositorio": repo_id,
                "media_commits_dia": round(media_commits_por_dia, 3),
            }
            resultados.append(commits_por_dia)
        page += 1

    return resultados


def commits_por_hora_func():
    headers = {"Authorization": f"token {config['TOKEN']}"}
    url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?per_page=100"
    resultados = []
    page = 1
    while True:
        paginated_repos_url = f"{url}&page={page}"
        repos_response = requests.get(paginated_repos_url, headers=headers)
        if repos_response.status_code != 200:
            raise HTTPException(
                status_code=repos_response.status_code,
                detail="Error al obtener los repositorios de la organización",
            )

        repos = repos_response.json()
        if not repos:
            break

        for repo in repos:
            repo_nombre = repo["name"]
            repo_id = repo["id"]
            commits_page = 1
            commit_hours = []
            while True:
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?per_page=100&page={commits_page}"
                commits_response = requests.get(commits_url, headers=headers)
                if commits_response.status_code != 200:
                    break

                repo_commits = commits_response.json()
                if not repo_commits:
                    break

                for commit in repo_commits:
                    commit_date = commit["commit"]["committer"]["date"]
                    commit_hour = datetime.strptime(
                        commit_date, "%Y-%m-%dT%H:%M:%SZ"
                    ).hour
                    commit_hours.append(commit_hour)

                commits_page += 1

            total_commits = len(commit_hours)
            if total_commits > 0:
                media_commits_por_hora = total_commits / 24.0
                commits_por_hora = {
                    "Repositorio": repo_nombre,
                    "id_repositorio": repo_id,
                    "media_commits_hora": round(media_commits_por_hora, 3),
                }
                resultados.append(commits_por_hora)

        page += 1

    return resultados


async def index_commits(repos_data, index_name):
    for repo in repos_data:
        doc_id = repo["id_repositorio"]
        try:
            existing_doc = es.get(index=index_name, id=doc_id)
            existing_data = existing_doc["_source"]
            existing_data.update(repo)
            es.update(index=index_name, id=doc_id, body={"doc": existing_data})
        except NotFoundError:
            es.index(index=index_name, id=doc_id, body=repo)
        except Exception as e:
            logging.error(f"Error al indexar documento en Elasticsearch: {e}")


async def index_commits_usu(repos_data, index_name):
    for repo_info in repos_data:
        try:

            doc_id = f"{repo_info['id_repositorio']}_{repo_info['usuario']}"

            existing_doc = es.get(index=index_name, id=doc_id)

            existing_data = existing_doc["_source"]
            existing_data["Repositorio"] = repo_info["Repositorio"]
            existing_data["commits"] = repo_info["commits"]
            es.update(index=index_name, id=doc_id, body={"doc": existing_data})
        except NotFoundError:
            es.index(
                index=index_name,
                id=doc_id,
                body={
                    "id_repositorio": repo_info["id_repositorio"],
                    "Repositorio": repo_info["Repositorio"],
                    "usuario": repo_info["usuario"],
                    "commits": repo_info["commits"],
                },
            )
        except Exception as e:
            logging.error(f"Error al indexar documento en Elasticsearch: {e}")
