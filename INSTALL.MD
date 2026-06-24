# Guía de instalación Happy Paws

## Prerequisitos

- Docker > 27.0

## Instrucciones de instalación

1. Instala Docker en tu computador a través de las [instruccion de instalación](https://docs.docker.com/engine/install/)
2. Copia y luego configura tus variables de entorno así

   ```bash
   cp .env.example .env
   ```

3. Construye tus contenedores con:

```bash
docker compose build
```

1.

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
