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

## Respaldos

En el VPS, dos timers de systemd respaldan la base de datos PostgreSQL ([#88](https://github.com/happypawspillaro/happypaws/issues/88)). Los archivos están en `config/respaldos/`. Son units **de usuario**: corren con el usuario que despliega el sitio, se instalan sin `sudo` y todo queda dentro de su carpeta personal, que sobrevive si se formatea `/`.

- **Diario (03:00):** `pg_dump` cifrado con [age](https://github.com/FiloSottile/age), guardado en `~/.local/state/happypaws-respaldo/respaldos/`. Se borran los de más de 30 días.
- **Mensual (día 1, 04:00):** hace un respaldo nuevo y lo sube a Google Drive con [rclone](https://rclone.org/drive/). En Drive se borran los de más de un año (van a la papelera de Drive).

El volcado pasa directo de `pg_dump` a `age`, así que nunca queda en texto plano en el disco. En el VPS solo está la clave **pública**. Así, aunque alguien entre al servidor, no puede descifrar los respaldos.

> Las fotos (volumen `media-volume`) todavía no se respaldan.

### Instalación

1. Instala `age` en tu computadora y `age` y `rclone` en el VPS. No vienen por defecto en Ubuntu:

   ```bash
   sudo apt install age          # en tu computadora
   sudo apt install age rclone   # en el VPS
   ```

2. En tu computadora (no en el VPS), genera el par de claves y guarda `respaldo.age` en un gestor de contraseñas. Sin esa clave no se puede restaurar nada:

   ```bash
   age-keygen -o respaldo.age
   ```

   El comando muestra la clave pública (`age1...`). Si quieres que más de una persona pueda restaurar, cada una genera su par y se pone una clave pública por línea.

3. En el VPS, con el usuario que despliega el sitio (debe estar en el grupo `docker`), copia la clave pública y la configuración:

   ```bash
   mkdir -p ~/.config/happypaws
   echo "age1..." > ~/.config/happypaws/respaldo.age.pub
   cp config/respaldos/respaldo.env.example ~/.config/happypaws/respaldo.env
   nano ~/.config/happypaws/respaldo.env   # ajustar REPO_DIR
   ```

4. Instala los units y prueba el respaldo diario:

   ```bash
   mkdir -p ~/.config/systemd/user
   cp config/respaldos/happypaws-respaldo*.{service,timer} ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user start happypaws-respaldo.service
   ls -l ~/.local/state/happypaws-respaldo/respaldos/
   ```

5. Configura Google Drive en rclone con un remoto llamado `gdrive`. La configuración queda en `~/.config/rclone/rclone.conf`. El VPS no tiene navegador, así que sigue las instrucciones de [rclone para máquinas remotas](https://rclone.org/remote_setup/):

   ```bash
   rclone config
   systemctl --user start happypaws-respaldo-nube.service
   ```

6. Activa los timers. Los timers de usuario solo corren mientras el usuario tiene una sesión abierta; `enable-linger` hace que corran siempre, también después de reiniciar el VPS (es el único paso con `sudo`):

   ```bash
   sudo loginctl enable-linger "$USER"
   systemctl --user enable --now happypaws-respaldo.timer happypaws-respaldo-nube.timer
   systemctl --user list-timers 'happypaws-*'
   ```

Los registros se ven con `journalctl --user -u happypaws-respaldo -u happypaws-respaldo-nube`.

### Restaurar

Con la clave privada `respaldo.age` y un archivo `.dump.age`:

```bash
age --decrypt --identity respaldo.age happypaws-AAAAMMDD-HHMMSS.dump.age |
  docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres \
  sh -c 'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

`--clean` borra lo que hay en la base antes de restaurar. Haz un respaldo de lo actual antes de usarlo.
