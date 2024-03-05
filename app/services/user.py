from fastapi import HTTPException
from app.schema.user import userSchema
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import requests
import os

load_dotenv()

GITHUB_API_URL = os.getenv('GITHUB_API_URL')
ORG = os.getenv('ORG')
TOKEN = os.getenv('TOKEN')

es = Elasticsearch("http://localhost:9200")

async def members_organization(): 
    all_members_data = []
    url = f"{GITHUB_API_URL}/orgs/{ORG}/members"

    headers = {"Authorization": f"token {TOKEN}"}
    params = {"per_page": 100, "page": 1} 
        
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
        
    members_data = response.json()

    for member in members_data:
        member_info = userSchema(**member)  
        all_members_data.append(member_info)
    
    return all_members_data

async def index_members_GrupoASD(all_members_data):
    for member_data in all_members_data:
        es.index(index="members_grupo-asd", id=member_data.id, document=member_data.dict())
    