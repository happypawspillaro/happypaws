#!/usr/bin/env bash
# Respaldo cifrado de la base de datos PostgreSQL (#88).
#
# Uso:
#   respaldo.sh local  Vuelca la base con pg_dump, la cifra con age y borra
#                      las copias locales de más de DIAS_RETENCION días.
#   respaldo.sh nube   Hace un respaldo local y lo sube con rclone.
#
# Lo ejecutan los timers de systemd de esta carpeta; ver INSTALL.md.
set -euo pipefail

: "${REPO_DIR:?Falta REPO_DIR, la carpeta del repositorio en el VPS}"
: "${AGE_DESTINATARIOS:?Falta AGE_DESTINATARIOS, el archivo con las claves públicas de age}"
DIR_RESPALDOS="${DIR_RESPALDOS:-${STATE_DIRECTORY:-/var/lib/happypaws-respaldo}/respaldos}"
DIAS_RETENCION="${DIAS_RETENCION:-30}"
RCLONE_DESTINO="${RCLONE_DESTINO:-gdrive:happypaws-respaldos}"

respaldo_local() {
	local destino
	destino="$DIR_RESPALDOS/happypaws-$(date +%Y%m%d-%H%M%S).dump.age"
	mkdir -p "$DIR_RESPALDOS"

	# El volcado pasa directo de pg_dump a age, así que nunca queda en texto
	# plano en el disco. Las variables se expanden dentro del contenedor.
	# shellcheck disable=SC2016
	if ! docker compose --project-directory "$REPO_DIR" \
		-f "$REPO_DIR/docker-compose.yml" -f "$REPO_DIR/docker-compose.prod.yml" \
		exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' |
		age --encrypt --recipients-file "$AGE_DESTINATARIOS" --output "$destino.tmp"; then
		rm -f "$destino.tmp"
		echo "Error: no se pudo generar el respaldo" >&2
		exit 1
	fi
	mv "$destino.tmp" "$destino"
	echo "Respaldo creado: $destino" >&2

	find "$DIR_RESPALDOS" -name 'happypaws-*.dump.age' -mmin +$((DIAS_RETENCION * 24 * 60)) -print -delete >&2

	echo "$destino"
}

respaldo_nube() {
	local archivo
	archivo="$(respaldo_local)"
	rclone copy "$archivo" "$RCLONE_DESTINO"
	echo "Subido a $RCLONE_DESTINO" >&2
}

case "${1:-}" in
local) respaldo_local >/dev/null ;;
nube) respaldo_nube ;;
*)
	echo "Uso: $0 local|nube" >&2
	exit 2
	;;
esac
