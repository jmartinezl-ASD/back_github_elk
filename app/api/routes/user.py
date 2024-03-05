from fastapi import APIRouter
from app.services.user import members_organization, index_members_GrupoASD
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/Users", tags=["Users"])

@router.get("/organization_members")
async def get_organization_members():
    all_members_data = await members_organization()
    try:
        members = await index_members_GrupoASD(all_members_data)
        return members
    except Exception as e:
        return print(f"No se pudo enviar datos a Elasticsearch: {e}")

# SISTEMATIZACIÓN RUTAS
    
@router.on_event("startup")
async def startup_event():
    await get_organization_members()
