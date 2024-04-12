from fastapi import APIRouter
from app.services.repositoryService import (
    service_Issues_repos,
    service_Pulls_repos,
    services_Branches_repos,
    service_Lenguajes_repos,
    services_repositorios_org,
    services_repos_inactivos_filtro,
    commits_repositorio,
    index_repos,
)


from app.services.repositoryOrgService import (
    service_repositorios_actividad,
    listar_todos_los_repositorios,
    rama_con_mas_commits,
    verificar_dependencias_desactualizadas,
)
from dotenv import load_dotenv
from datetime import datetime
from config import config
import logging
import os


load_dotenv()
ORG = os.getenv("ORG")
GITHUB_API_URL = os.getenv("GITHUB_API_URL")


router = APIRouter(prefix="/Repository", tags=["Repository"])


async def repetir_tareas_repositorio():
    logging.info("Módulo repositorios")
    logging.debug(f"El valor actual del TOKEN es: {config['TOKEN']}")
    await Issues_repositorio()
    await total_commits_repositorio()
    await lenguajes_repositorio()
    await ramas_repositorio()
    await pulls_repositorio()
    await repositorios_org()
    await mas_actividad()
    await inactivos()
    await dependencias_desactualizadas()


@router.get("/issues_repos")
async def Issues_repositorio():
    issues = await service_Issues_repos()
    try:
        await index_repos(issues, "data_github")
        return issues
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return issues


@router.get("/Lenguajes_repos")
async def lenguajes_repositorio():
    lenguajes = await service_Lenguajes_repos()
    try:
        await index_repos(lenguajes, "data_github")
        return lenguajes
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return lenguajes


@router.get("/branches_repos")
async def ramas_repositorio():
    branches = await services_Branches_repos()
    try:
        await index_repos(branches, "data_github")
        return branches
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return branches


@router.get("/Pulls_repos")
async def pulls_repositorio():
    pulls = await service_Pulls_repos()
    try:
        await index_repos(pulls, "data_github")
        return pulls
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return pulls


@router.get("/Org")
async def repositorios_org():
    repositorios = await services_repositorios_org()
    data = []
    for repo in repositorios:
        created_at = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        formatted_date = (
            created_at.strftime("%d-")
            + meses[created_at.month - 1]
            + created_at.strftime("-%Y")
        )
        repo_data = {
            "id_repositorio": repo["id"],
            "Repositorio": repo["name"],
            "Creación repositorio": formatted_date,
        }
        data.append(repo_data)
    try:
        await index_repos(data, "data_github")
        return data
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return data


@router.get("/Mas_Activo")
async def mas_actividad():
    actividad = await service_repositorios_actividad()
    try:
        await index_repos(actividad, "data_github")
        return actividad
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return {"Repositorio": actividad}


@router.get("/Inactivos")
async def inactivos():
    inactive_repos = await services_repos_inactivos_filtro()
    try:
        await index_repos(inactive_repos, "data_github")
        return inactive_repos
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return inactive_repos


@router.get("/dependencias-desactualizadas")
async def dependencias_desactualizadas():
    repositorios = await listar_todos_los_repositorios()
    resultado = []
    for repo in repositorios:
        nombre_repo = repo["name"]
        rama = await rama_con_mas_commits(nombre_repo)
        desactualizadas = await verificar_dependencias_desactualizadas(
            repo["name"], rama
        )
        resultado.append(
            {
                "id_repositorio": repo["id"],
                "Repositorio": repo["name"],
                "dependencias_desactualizadas": desactualizadas,
            }
        )
    try:
        await index_repos(resultado, "data_github")
        return resultado
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return resultado

@router.get("/total-commits")
async def total_commits_repositorio():
    todos_los_commits = await commits_repositorio()
    try:
        await index_repos(todos_los_commits, "data_github")
        return todos_los_commits
    except Exception as e:
        logging.error(f"Error: {e}")
        return {"error": "Error al obtener los commits de la rama por defecto"}
