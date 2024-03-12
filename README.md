# poc-github-elk

## poc-github-elk

1. Creacion del entorno virtual

- `python -m venv nombre_del_entorno`

2. Entrar en el entorno virtual

- `nombre_del_entorno\Scripts\activate`

3. Installar dependencias

- `pip install -r requests`

0. Para visualizar las dependencias de este proyecto, consulta el archivo requirements.txt con las siguientes lineas en la terminal

- `pip freeze requeriments.txt`
- `pip list`

4. Salir del entorno virtual

- `deactivate`

5. Ejecutar servidor local

- `uvicorn main:app --reload`

Documetation about GitHub Api Rest: https://docs.github.com/en/rest?apiVersion=2022-11-28

En resumen, al ejecutar tu aplicación FastAPI en el servidor local al que puedes acceder a ella a través de la dirección http://127.0.0.1:8000.

