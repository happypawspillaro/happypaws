# Guía de Desarrollo

En la presente guía, te introduce como poder desarrollar la página web de Happy Paws, es necesario primero instalar tal como dice la [Guía de instalación](INSTALL.MD)

## Configuraciones de desarrollo

Para poder realizar cambios tanto en scripts de Python como archivos web y verlos en tiempo real, inicializa tu entorno con el siguiente comando

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Incrementar la verbosidad

En caso necesites mayor detalle de los registros del sistema, cambia en el servicio `web`, en la sección `environment` la línea de `INFO` a `DEBUG` como en el siguiente ejemplo:

```yaml
- DJANGO_LOG_LEVEL=DEBUG
```
