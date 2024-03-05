# poc-github-elk
poc-github-elk

*En la terminal cmd* 

- Creacion del entorno virtual
python -m venv nombre_del_entorno
py -m venv venv

- Entrar en el entorno virtual
nombre_del_entorno\Scripts\activate
venv\Scripts\activate 

- Installar dependencias
pip install requests

- Ver dependecias
pip list

- Salir del entorno virtual
deactivate

- Ejecutar servidor local
uvicorn main:app --reload

Documetation about GitHub Rest: https://docs.github.com/en/rest?apiVersion=2022-11-28

-   informacion de los usuarios: 
1. Para buscar al usuario:
https://api.github.com/users/ { owner }

2. Para buscar los repositorios de un usuario:
https://api.github.com/users/ { owner } /repos

3. Para ver info relevante sobre el usuario: (requiere autenticacion)
https://api.github.com/users/ { owner } /hovercard

4. Para ver las llaves: (requiere autenticacion)
https://api.github.com/users/ { owner } /keys

1. Para buscar las ramas de un repositorio:
https://api.github.com/repos/ { owner } / { repo } /branches

2. Para ver los comits de un repositorio:
https://api.github.com/repos/ { owner } / { repo} /commits

3. Para ver los lenguajes de un repositorio:
https://api.github.com/repos/ { owner } / { repo } /languages

4. Para ver los problemas de un repositorio:
https://api.github.com/repos/ { owner} / { repo } /issues

5. Para ve la lista de todos los artefactos de un repositorio
https://api.github.com/repos/ { owner }/ { repo } /actions/artifacts

6. Para saber los eventos del repositorio
https://api.github.com/repos/ { owner } / { repo } /events

7. Para revisar la lista de pulls realizados
https://api.github.com/repos/ { owner } / { repo } /pulls 

8. Para ver una lista de releases
https://api.github.com/repos/ { owner } / { repo } /releases

9. Para ver los colaboradores de un repositorio: (requiere autenticacion)
https://api.github.com/repos/ { owner} / { repo } /collaborators

10. Para ver el contenido de un repositorio
https://api.github.com/repos/ { owner } / { repo } /contents
https://api.github.com/repos/ { owner } / { repo } /contents / { path }

-  informacion de la empresa:     

1. lista de organizaciones:
https://api.github.com/organizations

2. informacion de la cuenta empresarial: 
https://api.github.com/orgs/ { org }

3. miembros relacionados:
https://api.github.com/orgs/ { org } /members
https://api.github.com/orgs/ { org } /public_members

4. gestion de equipos y permisos: (requiere autenticacion)
https://api.github.com/orgs/ { org } /teams

5. visualizar la lista de usuarios blokeados por la organizacion: (requiere autenticacion)
https://api.github.com/orgs/ { org } /blocks

6. visualizacion de los repositorios:
https://api.github.com/orgs/ { org } /repos

7. ver lista de proyectos
https://api.github.com/orgs/ { org } /projects

8. ver la lista de colaboradores por proyecto
https://api.github.com/orgs/ { org } /projects/ { project_id } /collaborators

En resumen, esta parte del código se encarga de ejecutar tu aplicación FastAPI en el servidor local para que puedas acceder a ella a través de la dirección http://localhost:8000.