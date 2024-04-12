from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import commits, user, repository
from app.api.routes.user import repetir_tareas_usuario
from app.api.routes.commits import repetir_tareas_commits
from app.api.routes.repository import repetir_tareas_repositorio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from config import config
from datetime import datetime
import logging
import os


app = FastAPI(title="github-elk", version="1.0.0", contact={"name": "github-elk"})
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposición de rutas para pruebas
# app.include_router(repository.router, prefix="/api")
# app.include_router(commits.router, prefix="/api")
# app.include_router(user.router, prefix="/api")


@app.post("/update-token")
async def update_token(new_token: str):
    global config
    if "TOKEN" in os.environ:
        os.environ["TOKEN"] = new_token
        config["TOKEN"] = new_token

        with open(".env", "r") as file:
            lines = file.readlines()
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith("TOKEN="):
                    file.write(f"TOKEN='{new_token}'\n")
                else:
                    file.write(line)
        return {"message": "Token actualizado correctamente"}
    else:
        return {"message": "La variable de entorno 'TOKEN' no existe"}


async def tareas_programadas():
    logging.info(f"Tarea ejecutada a las {datetime.now()}")
    await repetir_tareas_usuario()
    await repetir_tareas_repositorio()
    await repetir_tareas_commits()
    logging.info(f"Tareas terminadas a las {datetime.now()}")


@app.on_event("startup")
async def startup_event():
    logging.info("FastApi en ejecución")
    load_dotenv()
    scheduler = AsyncIOScheduler(timezone="America/Bogota")
    scheduler.add_job(
        tareas_programadas, CronTrigger(hour=10, minute=59), id="tareas_programadas"
    )
    scheduler.start()
