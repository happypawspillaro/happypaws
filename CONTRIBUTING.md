# Guía de Contribución

En la presente guía, te introduce como poder desarrollar la página web de Happy Paws, es necesario primero instalar tal como dice la [Guía de instalación](INSTALL.MD)

## Flujo de desarrollo

Se recomienda el siguiente flujo de desarrollo en el proyecto

- _(Opcional)_ Añadir un nuevo [Issue](https://github.com/happypawspillaro/happypaws/issues) describiendo el cambio que se pretende hacer
- Crear una nueva rama en base a la `main`.
- Cumplir el [Formato de código](#formato-de-código) del proyecto.
- Crear un nuevo `Pull request`, pasar las pruebas de formato y regresión y aceptar tu contribución por un revisor.

## Configuraciones de desarrollo

Para poder realizar cambios tanto en scripts de Python como archivos web y verlos en tiempo real, inicializa tu entorno con el siguiente comando:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml build
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Exponer puertos

Si necesitas, por ejemplo exponer puertos en producción para revisar datos con un programa como `DBeaver`, usa la función de [Docker Compose Override](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/), siguiendo este ejemplo:

1. Crea un nuevo archivo, en este caso `docker-compose.prod.override.yml`

   ```bash
   touch docker-compose.prod.override.yml
   ```

2. Añade el siguiente código dentro del nuevo archivo

   ```yaml
   services:
   postgres:
     ports:
       - 5432:5432
   ```

3. Comprueba que el puerto está abierto con:

   ```bash
   docker compose -f docker-compose.yml -f docker-compos
   e.prod.yml ps
   ```

### Incrementar la verbosidad

En caso necesites mayor detalle de los registros del sistema, descomenta en tu archivo `.env` la línea, mas información en la [guía de variables de entorno](REFERENCE.md#variables-de-entorno):

```dotenv
DJANGO_LOG_LEVEL=DEBUG
```

## Formato de Código

Como buenas prácticas de código para un fácil mantenimiento y colaboración, se sugiere ajustarse al formato de código usado en el proyecto, éste se divide entre código de Python y del Frontend, para saber como configurar tus formateadores d código, revisa las siguientes subsecciones:

### Python

Para formatear tus archivos de Python, sigue las siguientes instrucciones:

1. Crea un nuevo o usa tu ambiente de Python e instala los formateadores con el siguiente comando:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install black flake8 flake8-pyproject isort pylint pylint-django
   # Permite ejecutar el script
   sudo chmod +x linters.sh
   ```

2. Puedes ejecutar todos los formateadores de una pasada con el script `linters.sh` y especificando como argumento tu script de Python

   ```bash
   ./linters.sh carpeta/codigo.py
   ```

### Frontend

Para formatear y ver errores de código en JavaScript, JSON, CSS, etc. puedes usar las herramientas como `prettier` o `biome`, los puedes instalar así como se muestra en los siguientes pasos:

1. Instala `nodejs` junto las herramientas con `npm` y `npx`, por ejemplo en Ubuntu:

   ```bash
   sudo apt update && sudo apt install nodejs
   ```

2. Instala los formateadores necesarios, por ejemplo en Ubuntu

   ```bash
   npm install --save-dev --save-exact @biomejs/biome prettier
   ```

3. Puedes usar los formateadores de la siguiente forma

   ```bash
   # Formatea y escribe el código
   npx prettier --write CONTRIBUTING.md
   # Formatear código
   npx biome format app/static/js/file.js
   # Verificar errores
   npx biome lint app/static/js/file.js
   ```
