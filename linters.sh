#!/usr/bin/bash

# Verificar si se pasó un archivo
if [ -z "$1" ]; then
	echo "Error: Debes proporcionar un archivo de Python válido."
	echo "Uso: $0 <archivo.py>"
	exit 1
fi

FILE="$1"

# 1. Ordenar imports en los scripts
echo "--- Ejecutando isort ---"
isort "$FILE"

# 2. Formatear estilo
echo "--- Ejecutando black ---"
black "$FILE"

# 3. Analizar calidad de códig (si uno falla, podemos detener o continuar)
echo "--- Ejecutando flake8 ---"
flake8 "$FILE"

echo "--- Ejecutando pylint ---"
pylint "$FILE"

echo "¡Proceso completado!"
