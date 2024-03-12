from fastapi import APIRouter, HTTPException
from app.services.user import miembros_organización_servicio, index_members_GrupoASD, miembros_activos_servicio
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()
router = APIRouter(prefix="/Users", tags=["Usuarios"])

@router.get("/miembros_grupoASD")
async def miembros_grupoASD():
    miembros_data = await miembros_organización_servicio()
    try:
        await index_members_GrupoASD(miembros_data)
    except Exception as e:
        print(f"No se pudo enviar datos a Elasticsearch: {e}")
        return miembros_data
    
@router.get("/miembros_activos")
async def miembros_activos():
    try:
        miembros_activos = await miembros_activos_servicio()
        return miembros_activos
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# SISTEMATIZACIÓN RUTAS
    
# @router.on_event("startup")
# async def startup_event():
#     await get_organization_members()  
#     print("La aplicación ha iniciado y se ha conectado a Elasticsearch.")

