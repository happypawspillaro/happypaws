# Guía de instalación Happy Paws

## Prerequisitos

- Docker > 27.0
- Git > 2.43

## Instrucciones de instalación

1. Instala Docker en tu computador a través de las instrucciones de  [instalación](https://docs.docker.com/engine/install/) para tu plataforma.
2. Clona este repositorio y cambia de directorio hacia el proyecto, lo puedes hacer con el siguiente comando:

    ```bash
    git clone https://github.com/happypawspillaro/happypaws.git
    cd happypaws
    ```

3. Copia y luego configura tus variables de entorno así:

   ```bash
   cp .env.example .env
   ```

4. Construye tus contenedores con:

    ```bash
    docker compose build
    ```

5. Inicia la configuración base de los contenedores con

    ```bash
    docker compose up -d
    ```

6. Antes de inicializar tu página y si es primera vez, sigue las instrucciones para generar [migraciones](#migraciones) y crear un [superusuario](#superusuario).
7. Abre el siguiente URL [http://localhost:8000](http://localhost:8000), si es que vez una página renderizada, esta correcto

## Migraciones

1. Para ejecutar tus migraciones, sea por primera vez o por cambio de los modelos, por favor ejecuta

```bash
docker compose -f docker-compose.yml -f docker-compose.migrate.yml up
```

## Superusuario

Un superusario es el usuario maestro que puede controlar todo el sistema, para crearlo por favor sigue las siguientes instrucciones

1. Crea un archivo de superusuario en la carpeta `credenciales/superuser/password.txt`, te recomendamos una contraseña segura, puedes crearlo  con:

```bash
    mkdir -p credenciales/superuser
    openssl rand -base64 32 > credenciales/superuser/password.txt
```

1. Crea el superusuario en tu proyecto con el comando

```bash
docker compose -f docker-compose.yml -f docker-compose.superuser.yml up
```
