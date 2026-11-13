#!/usr/bin/env bash
# Respaldo cifrado de la base de datos PostgreSQL (#88).
#
# Uso:
#   respaldo.sh local  Vuelca la base con pg_dump, la cifra con age y borra
#                      las copias locales de más de DIAS_RETENCION días.
#   respaldo.sh nube   Hace un respaldo local, lo sube con rclone y borra las
#                      copias de la nube de más de DIAS_RETENCION_NUBE días.
#
# Lo ejecutan los timers de systemd (de usuario) de esta carpeta; ver INSTALL.md.
set -euo pipefail

: "${REPO_DIR:?Falta REPO_DIR, la carpeta del repositorio en el VPS}"
AGE_DESTINATARIOS="${AGE_DESTINATARIOS:-$HOME/.config/happypaws/respaldo.age.pub}"
DIR_RESPALDOS="${DIR_RESPALDOS:-${STATE_DIRECTORY:-$HOME/.local/state/happypaws-respaldo}/respaldos}"
DIAS_RETENCION="${DIAS_RETENCION:-30}"
DIAS_RETENCION_NUBE="${DIAS_RETENCION_NUBE:-365}"
RCLONE_DESTINO="${RCLONE_DESTINO:-gdrive:happypaws-respaldos}"

comprobar_destinatarios() {
	# Sin una clave age1... válida, age falla con un error poco claro.
	if ! grep -qE '^age1[0-9a-z]+$' "$AGE_DESTINATARIOS" 2>/dev/null; then
		echo "Error: $AGE_DESTINATARIOS no tiene una clave pública de age (age1...)" >&2
		exit 1
	fi
}

comprobar_destino_nube() {
	# Sin ":", rclone lo toma como una carpeta local y el respaldo no sale del VPS.
	if [[ $RCLONE_DESTINO != *:* ]]; then
		echo "Error: RCLONE_DESTINO debe tener la forma remoto:carpeta (p. ej. gdrive:happypaws-respaldos), no '$RCLONE_DESTINO'" >&2
		exit 1
	fi
}

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
	# Siempre se sube el respaldo recién creado, no el más reciente de la carpeta.
	archivo="$(respaldo_local)"
	rclone copy "$archivo" "$RCLONE_DESTINO"
	echo "Subido a $RCLONE_DESTINO" >&2

	# rclone copy conserva la fecha del archivo local, que es la de creación.
	rclone delete "$RCLONE_DESTINO" --include 'happypaws-*.dump.age' \
		--min-age "${DIAS_RETENCION_NUBE}d" -v
}

case "${1:-}" in
local)
	comprobar_destinatarios
	respaldo_local >/dev/null
	;;
nube)
	comprobar_destinatarios
	comprobar_destino_nube
	respaldo_nube
	;;
*)
	echo "Uso: $0 local|nube" >&2
	exit 2
	;;
esac
