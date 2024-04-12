from datetime import datetime, timedelta
from app.services.repositoryService import services_repositorios_org
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from config import config
import xml.etree.ElementTree as ET
import requests
import semver
import base64
import json
import os
import re


load_dotenv()

ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME").strip()
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD").strip()
ORG = os.getenv("ORG").strip()

es = Elasticsearch(
    [ELASTIC_SEARCH_URL], http_auth=(ELASTICSEARCH_USERNAME, ELASTIC_PASSWORD)
)


async def obtener_ramas(repo):
    headers = {"Authorization": f"token {config['TOKEN']}"}
    ramas = []
    page = 1
    while True:
        url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo}/branches?per_page=100&page={page}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            ramas_data = response.json()
            if not ramas_data:
                break
            for rama in ramas_data:
                ramas.append(rama["name"])
            page += 1
        except requests.exceptions.RequestException as e:
            return None
    return ramas


async def contar_commits_recientes(repo, rama, desde):
    url_base = (
        f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo}/commits?sha={rama}"
    )
    headers = {"Authorization": f"token {config['TOKEN']}"}
    commits_recientes = 0
    url = f"{url_base}&since={desde}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commits_recientes = len(response.json())
        while "next" in response.links:
            response = requests.get(response.links["next"]["url"], headers=headers)
            response.raise_for_status()
            commits_recientes += len(response.json())
    except requests.exceptions.RequestException as e:
        return None
    return commits_recientes


async def contar_commits_activo(repo, rama):
    query = """
    query($repo: String!, $owner: String!, $branch: String!) {
      repository(name: $repo, owner: $owner) {
        ref(qualifiedName: $branch) {
          target {
            ... on Commit {
              history {
                totalCount
              }
            }
          }
        }
      }
    }
    """
    variables = {"repo": repo, "owner": ORG, "branch": rama}
    headers = {"Authorization": f"Bearer {config['TOKEN']}"}
    response = requests.post(
        f"{config['GITHUB_API_URL']}/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
    )
    if response.status_code == 200:
        data = response.json()
        total_commits = data["data"]["repository"]["ref"]["target"]["history"][
            "totalCount"
        ]
        return total_commits
    else:
        raise Exception(f"Error HTTP {response.status_code}: {response.text}")


async def service_repositorios_actividad():
    repositorios = await services_repositorios_org()
    if not repositorios:
        return {"error": "No se encontraron repositorios para la organización"}
    actividad_repos = []
    for repo in repositorios:
        id_repo = repo["id"]
        nombre_repo = repo["name"]
        ramas = await obtener_ramas(nombre_repo)
        rama_con_mas_commits = ""
        rama_con_mas_commits_semana = ""
        max_commits = 0
        max_commits_semana = 0
        commits_ultima_semana = 0
        desde = (datetime.now() - timedelta(days=7)).isoformat()
        for rama in ramas:
            total_commits = await contar_commits_activo(nombre_repo, rama)
            if total_commits > max_commits:
                max_commits = total_commits
                rama_con_mas_commits = rama

            commits_recientes = await contar_commits_recientes(nombre_repo, rama, desde)
            if commits_recientes > max_commits_semana:
                max_commits_semana = commits_recientes
                rama_con_mas_commits_semana = rama
                commits_ultima_semana = commits_recientes
        actividad_repos.append(
            {
                "id_repositorio": id_repo,
                "Repositorio": nombre_repo,
                "rama_con_mas_commits": rama_con_mas_commits,
                "rama_con_mas_commits_semana": rama_con_mas_commits_semana,
                "commits_ultima_semana": commits_ultima_semana,
            }
        )
    actividad_repos_ordenada = sorted(
        actividad_repos, key=lambda x: x["commits_ultima_semana"], reverse=True
    )
    return actividad_repos_ordenada


async def contar_commits(repo, rama):
    query = """
    query {
      repository(owner: "{owner}", name: "{repo}") {
        ref(qualifiedName: "refs/heads/{branch}") {
          target {
            ... on Commit {
              history {
                totalCount
              }
            }
          }
        }
      }
    }
    """
    query = (
        query.replace("{owner}", repo.split("/")[0])
        .replace("{repo}", repo.split("/")[1])
        .replace("{branch}", rama)
    )
    headers = {"Authorization": f"Bearer {config['TOKEN']}"}
    try:
        response = requests.post(
            f"{config['GITHUB_API_URL']}/graphql",
            json={"query": query},
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        total_commits = data["data"]["repository"]["ref"]["target"]["history"][
            "totalCount"
        ]
    except requests.exceptions.RequestException as e:
        total_commits = 0
    return total_commits


async def descargar_archivo_dependencias(repo, rama, archivo):
    url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo}/contents/{archivo}?ref={rama}"
    headers = {"Authorization": f"token {config['TOKEN']}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()
        if "content" in content:
            if (
                archivo.endswith((".txt", ".xml", "gemfile"))
                or archivo == "packages.config"
            ):
                return base64.b64decode(content["content"]).decode("utf-8")
            elif archivo.endswith(".json"):
                return json.loads(base64.b64decode(content["content"]).decode("utf-8"))
    except requests.exceptions.RequestException as e:
        return None


async def comparar_dependencias(dependencias):
    desactualizadas = []
    for dependencia in dependencias:
        if "==" not in dependencia:
            continue
        nombre, version = dependencia.split("==")
        ultima_version = await obtener_ultima_version_pypi(nombre)
        if version != ultima_version:
            desactualizadas.append(
                {
                    "dependencia": nombre,
                }
            )
    return desactualizadas


async def obtener_ultima_version_pypi(nombre):
    url = f"https://pypi.org/pypi/{nombre}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.exceptions.RequestException as e:
        return None


async def verificar_dependencias_desactualizadas(repo, rama):

    dependencias_python = await descargar_archivo_dependencias(
        repo, rama, "requirements.txt"
    )
    if dependencias_python:
        dependencias = dependencias_python.split("\n")
        desactualizadas = await comparar_dependencias(dependencias)
        if desactualizadas:
            return len(desactualizadas)

    config_content = await descargar_archivo_dependencias(repo, rama, "packages.config")
    if config_content:
        desactualizadas = await comparar_dependencias_packages_config(config_content)
        if desactualizadas:
            return len(desactualizadas)

    gemfile_content = await descargar_archivo_dependencias(repo, rama, "gemfile")
    if gemfile_content:
        desactualizadas = await comparar_dependencias_ruby(gemfile_content)
        if desactualizadas:
            return len(desactualizadas)

    pom_xml = await descargar_archivo_dependencias(repo, rama, "pom.xml")
    if pom_xml:
        desactualizadas = await comparar_dependencias_maven(pom_xml)
        if desactualizadas:
            return len(desactualizadas)

    package_json = await descargar_archivo_dependencias(repo, rama, "package.json")
    if package_json:
        desactualizadas = []
        if "dependencies" in package_json:
            desactualizadas.extend(
                await comparar_dependencias_node(package_json["dependencies"])
            )
        if "devDependencies" in package_json:
            desactualizadas.extend(
                await comparar_dependencias_node(package_json["devDependencies"])
            )
        return len(desactualizadas)

    composer_json = await descargar_archivo_dependencias(repo, rama, "composer.json")
    if composer_json:
        desactualizadas = []
        if "require" in composer_json:
            desactualizadas.extend(
                await comparar_dependencias_composer(composer_json["require"])
            )
        if "require-dev" in composer_json:
            desactualizadas.extend(
                await comparar_dependencias_composer(composer_json["require-dev"])
            )
        return len(desactualizadas)

    return []


async def rama_con_mas_commits(repo):
    query = """
     query($repo: String!, $owner: String!) {
      repository(name: $repo, owner: $owner) {
        refs(refPrefix: "refs/heads/", first: 100) {
          edges {
            node {
              name
              target {
                ... on Commit {
                  history(first: 1) {
                    totalCount
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"repo": repo, "owner": ORG}
    headers = {"Authorization": f"Bearer {config['TOKEN']}"}
    rama_max_commits = ""
    max_commits = -1
    try:
        response = requests.post(
            f"{config['GITHUB_API_URL']}/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        for edge in data["data"]["repository"]["refs"]["edges"]:
            rama = edge["node"]
            commits = rama["target"]["history"]["totalCount"]
            if commits > max_commits:
                max_commits = commits
                rama_max_commits = rama["name"]
    except requests.exceptions.RequestException as e:
        return None
    return rama_max_commits


async def listar_todos_los_repositorios():
    repos = []
    page = 1
    while True:
        url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?per_page=100&page={page}"
        headers = {"Authorization": f"token {config['TOKEN']}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_data = response.json()
        if not page_data:
            break
        for repo in page_data:
            repos.append({"id": repo["id"], "name": repo["name"]})
        page += 1
    return repos


async def comparar_dependencias_node(dependencias):
    desactualizadas = []
    for nombre, version in dependencias.items():
        ultima_version = await obtener_ultima_version_npm(nombre)
        if version.strip("^~") != ultima_version:
            desactualizadas.append({"dependencia": nombre})
    return desactualizadas


async def obtener_ultima_version_npm(nombre):
    url = f"https://registry.npmjs.org/{nombre}/latest"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["version"]
    except requests.exceptions.RequestException as e:
        return None


async def comparar_dependencias_composer(dependencias):
    desactualizadas = []
    for nombre, version in dependencias.items():
        ultima_version = await obtener_ultima_version_composer(nombre)
        if version.strip("^~") != ultima_version:
            desactualizadas.append({"dependencia": nombre})
    return desactualizadas


async def obtener_ultima_version_composer(nombre):
    url = f"https://repo.packagist.org/p2/{nombre}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        versiones = data["packages"][nombre]
        ultima_version = versiones[0]["version"]
        return ultima_version
    except requests.exceptions.RequestException as e:
        return None


async def comparar_dependencias_maven(pom_content):
    desactualizadas = []
    root = ET.fromstring(pom_content)
    namespaces = {"m": "http://maven.apache.org/POM/4.0.0"}
    for dependency in root.findall(".//m:dependency", namespaces):
        groupId = dependency.find("m:groupId", namespaces).text
        artifactId = dependency.find("m:artifactId", namespaces).text
        version = dependency.find("m:version", namespaces).text
        if version.startswith("${"):
            continue
        ultima_version = await obtener_ultima_version_maven(groupId, artifactId)
        if version != ultima_version:
            desactualizadas.append({"dependencia": f"{groupId}:{artifactId}"})
    return desactualizadas


async def obtener_ultima_version_maven(groupId, artifactId):
    url = f"https://search.maven.org/solrsearch/select?q=g:%22{groupId}%22+AND+a:%22{artifactId}%22&rows=1&wt=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["response"]["numFound"] > 0:
            ultima_version = data["response"]["docs"][0]["latestVersion"]
            return ultima_version
        return ultima_version
    except requests.exceptions.RequestException as e:
        return None


async def obtener_ultima_version_rubygem(gema):
    url = f"https://rubygems.org/api/v1/gems/{gema}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["version"]
    except requests.exceptions.RequestException as e:
        return None


async def comparar_dependencias_ruby(gemfile_content):
    desactualizadas = []
    regex = r"gem ['\"](\w+)['\"], ['\"]~> (.+?)['\"]"
    matches = re.findall(regex, gemfile_content)
    for match in matches:
        gema, version_requerida = match
        ultima_version = await obtener_ultima_version_rubygem(gema)
        if ultima_version and not await version_es_compatible(
            version_requerida, ultima_version
        ):
            desactualizadas.append({"gema": gema})
    return desactualizadas


async def version_es_compatible(version_requerida, ultima_version):
    try:
        version_base = semver.VersionInfo.parse(version_requerida)
        version_siguiente_minor = version_base.bump_minor()
        rango_permitido = f">={version_base} <{version_siguiente_minor.major}.{version_siguiente_minor.minor}.0"
        return semver.match(ultima_version, rango_permitido)
    except ValueError as e:
        return False


async def comparar_dependencias_packages_config(config_content):
    desactualizadas = []
    root = ET.fromstring(config_content)

    for package in root.findall(".//package"):
        package_id = package.attrib.get("id")
        version_actual = package.attrib.get("version")

        if package_id and version_actual:
            ultima_version = await obtener_ultima_version_nuget(package_id)
            if ultima_version and version_actual != ultima_version:
                desactualizadas.append({"paquete": package_id})
    return desactualizadas


async def obtener_ultima_version_nuget(paquete_id):
    url = "https://api.nuget.org/v3/registration5-gz-semver2/microsoft.extensions.dependencyinjection/index.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        versiones = []
        for page in data["items"]:
            for item in page["items"]:
                version = item["catalogEntry"]["version"]
                versiones.append(version)

        if not versiones:
            return None
        ultima_version = sorted(
            versiones,
            key=lambda x: [
                int(y) if y.isdigit() else y for y in x.replace("-", ".").split(".")
            ],
        )[-1]
        return ultima_version
    except Exception as e:
        return None
