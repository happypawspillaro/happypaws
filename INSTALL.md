# Guía de instalación Happy Paws

## Prerequisitos

- Docker > 27.0
- Git > 2.43

## Instrucciones de instalación

1. Instala Docker en tu computador a través de las instrucciones de [instalación](https://docs.docker.com/engine/install/) para tu plataforma.
2. Clona este repositorio y cambia de directorio hacia el proyecto, lo puedes hacer con el siguiente comando:

   ```bash
   git clone https://github.com/happypawspillaro/happypaws.git
   cd happypaws
   ```

3. Copia tus variables de entorno locales, por ejemplo en Linux:

   ```bash
   cp .env.example .env
   ```

   Luego, ajustales a conveniencia, puedes guiarte en la [guía de referencia](REFERENCE.md#variables-de-entorno) para más información.

4. Crea tus credenciales seguras usadas por [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) para inicializar los datos sensibles, por ejemplo en Linux:

   ```bash
   mkdir -p credenciales/database
   openssl rand -base64 32 > credenciales/postgres/password.txt
   mkdir -p credenciales/superuser
   openssl rand -base64 32 > credenciales/superuser/password.txt
   ```

5. Construye tus contenedores con:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml build
   ```

6. Inicia la configuración base de los contenedores con

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml -d
   ```

7. Antes de inicializar tu página y si es primera vez, sigue las instrucciones para generar [migraciones](#migraciones) y crear un [superusuario](#superusuario).
8. Abre el siguiente URL `https://localhost:<NGINX_HTTPS_PORT>`, si es que todo salió bien podrás ver la página web inicial.

## Migraciones

1. Para ejecutar tus migraciones, sea por primera vez o por cambio de los modelos, por favor ejecuta:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.migrate.yml up
```

## Superusuario

Un superusario es el usuario maestro que puede controlar todo el sistema, para crearlo por favor sigue las siguientes instrucciones

1. Crea el superusuario en tu proyecto con el comando:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.superuser.yml up
```
