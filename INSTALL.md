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

   Luego, ajustales a conveniencia(no olvides añadir tu `SECRET_KEY`), puedes guiarte en la [guía de referencia](REFERENCE.md#variables-de-entorno) para más información.

4. Crea tus credenciales seguras usadas por [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) para inicializar los datos sensibles, por ejemplo en Linux:

   ```bash
   mkdir -p credenciales/postgres
   openssl rand -base64 32 > credenciales/postgres/password.txt
   mkdir -p credenciales/superuser
   openssl rand -base64 32 > credenciales/superuser/password.txt
   ```

5. Crea un certificado TLS, sigue la documentación de [Certificados TLS](#certificados-tls) para saber como crearlos, por ejemplo de forma [local](#local)
6. Construye tus contenedores con:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml build
   ```

7. Inicia la base de datos primero:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up postgres -d
   ```

8. Antes de inicializar tu página y si es primera vez, sigue las instrucciones para generar [migraciones](#migraciones) y crear un [superusuario](#superusuario).

9. Colecciona los archivos estáticos con el siguiente comando

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml exec web python manage.py collectstatic
   ```

10. Finalmente inicializa los demás contenedores con:

    ```bash
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    ```

11. Abre el siguiente URL [https://localhost:8443](https://localhost:8443) (a menos que hayas cambiado la variable `NGINX_HTTPS_PORT` en tu `.env`), si es que todo salió bien podrás ver la página web inicial.

_Opcional_: Usa la sección [Inicializar datos](#inicializar-datos) para importar datos existentes a tu base de datos.

## Migraciones

1. Para ejecutar tus migraciones, sea por primera vez o por cambio de los modelos, por favor ejecuta:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.migrate.yml up web
   ```

## Superusuario

Un superusario es el usuario maestro que puede controlar todo el sistema, para crearlo por favor sigue las siguientes instrucciones

1. Crea el superusuario en tu proyecto con el comando:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.superuser.yml up web
   ```

## Certificados TLS

Para encriptar y autenticar tráfico HTTPS via TLS(SSL) necesitamos un [certificado](https://letsencrypt.org/docs/glossary/#def-certificate), para el presente proyecto se lo puede obtener de estas formas:

### Local

Puedes crear tu certificado local que debe ser usado en modo desarrollo, lo puedes hacer a través de este comando de Linux

```bash
mkdir -p web/ssl
openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes \
    -keyout web/ssl/happypaws.key -out web/ssl/happypaws.crt \
    -subj '/CN=*.happypawspillaro.org' \
    -addext 'subjectAltName=DNS:*.happypawspillaro.org'
```

## Inicializar datos

Por favor descarga los datos de la carpeta [Datos Página Web](https://drive.google.com/drive/folders/1T8PljxUi260mTUeI1EIXsNTZgHS7pwOl?usp=sharing) y descomprimelos en la ruta principal del proyecto, por ejemplo:

```bash
happypaws/
├── datos_happy_paws.json
├── Datos Página Web.ods
├── docs_to_seed.py
├── imagenes_happy_paws
│   ├── Adopciones
│   │   ├── Anastasia.jpg
│   │   └── Sol.jpg
│   ├── CasosMédicos
│   │   ├── Bruce.jpg
│   │   └── Lulu.jpg
│   └── Reportes
│       ├── Amarilla.jpg
│       └── Saco.jpg
```

Luego, inicializa el `seed_demo`, montando la carpeta de imágenes y datos con el comando:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm \
  -v "$(pwd)/datos_happy_paws.json:/tmp/seed_data/datos.json" \
  -v "$(pwd)/imagenes_happy_paws:/tmp/seed_data/imagenes" \
  web python3 manage.py seed_demo \
  --ruta-datos /tmp/seed_data/datos.json \
  --ruta-imagenes /tmp/seed_data/imagenes
```

Luego, carga de nuevo tu contenedor `web` con:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up nginx web --build -d
```
