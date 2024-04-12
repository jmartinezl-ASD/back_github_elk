from elasticsearch import Elasticsearch
from fastapi import HTTPException
from dotenv import load_dotenv
from config import config
import requests
import os

load_dotenv()

ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME").strip()
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD").strip()


es = Elasticsearch(
    [ELASTIC_SEARCH_URL], http_auth=(ELASTICSEARCH_USERNAME, ELASTIC_PASSWORD)
)


async def miembros_organización_servicio():
    miembros_data = []
    headers = {"Authorization": f"token {config['TOKEN']}"}
    page = 1
    while True:
        url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/members?state=all&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        data = response.json()
        if not data:
            break
        for miembro in data:
            info_miembro = {
                "id_usuario": miembro["id"],
                "usuario": miembro["login"],
                "tipo": miembro["type"],
            }
            miembros_data.append(info_miembro)
        page += 1
    return miembros_data


async def miembros_activos_servicio():
    headers = {"Authorization": f"token {config['TOKEN']}"}
    repos_url = (
        f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?state=all&per_page=100"
    )
    colaboradores_info = {}

    page = 1
    while True:
        paginated_repos_url = f"{repos_url}&page={page}"
        response = requests.get(paginated_repos_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al traer a los miembros más activos",
            )

        repos = response.json()
        if not repos:
            break

        for repo in repos:
            repo_nombre = repo["name"]
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
                    colaboraciones = colaborador["contributions"]
                    id_colaborador = colaborador["id"]
                    if login in colaboradores_info:
                        colaboradores_info[login][
                            "total_contributions"
                        ] += colaboraciones
                        colaboradores_info[login]["repositories"].append(
                            {"Nombre": repo_nombre, "Contribuciones": colaboraciones}
                        )
                    else:
                        colaboradores_info[login] = {
                            "id": id_colaborador,
                            "total_contributions": colaboraciones,
                            "repositories": [
                                {
                                    "Nombre": repo_nombre,
                                    "Contribuciones": colaboraciones,
                                }
                            ],
                        }

                contribs_page += 1

        page += 1

    colaboradores_activos_data = []

    for login, info in colaboradores_info.items():
        colaboradores_activos_data.append(
            {
                "id_usuario": info["id"],
                "usuario": login,
                "Total contribuciones": info["total_contributions"],
                "Repositorios": info["repositories"],
            }
        )

    return colaboradores_activos_data


async def index_miembros(miembros_data, index_name):
    for member_data in miembros_data:
        es.index(index=index_name, id=member_data["id_usuario"], document=member_data)
