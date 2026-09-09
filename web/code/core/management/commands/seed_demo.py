import json
from datetime import datetime, time
from pathlib import Path

from adoptions.models import (
    AdoptionApplication,
    EstadoSolicitud,
    PropositoTenencia,
    TipoVivienda,
)
from animals.models import Animal, Especie, EstadoAnimal, Origen, Sexo, Tamano
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from medical_cases.models import (
    CasePhoto,
    CaseUpdate,
    CategoriaEgreso,
    Donation,
    EstadoCaso,
    Expense,
    MedicalCase,
)
from reports.models import (
    EspecieMascota,
    EstadoReporte,
    Report,
    ReportComment,
    ReportPhoto,
    ReportSighting,
    SexoMascota,
    TipoReporte,
)

User = get_user_model()

KEY2ENUM = {
    "Animales": {
        "especie": Especie,
        "sexo": Sexo,
        "tamano": Tamano,
        "origen": Origen,
        "estado": EstadoAnimal,
    },
    "SolicitudesAdopciones": {
        "tipo_vivienda": TipoVivienda,
        "estado": EstadoSolicitud,
        "proposito": PropositoTenencia,
    },
    "Caso Médico": {
        "estado": EstadoCaso,
    },
    "Gastos": {
        "categoria": CategoriaEgreso,
    },
    "Reportes": {
        "tipo": TipoReporte,
        "estado": EstadoReporte,
        "especie": EspecieMascota,
        "sexo": SexoMascota,
    },
}


def convertir_key_a_enum(dato: dict, key_enum_dict: dict):
    """Convierte una clave de diccionario plana a su correspondiente enum.

    Args:
        dato (dict): Diccionario que contiene tus datos.
        key_enum_dict (dict): Diccionario en formato key: Enum para transformar tus valores.
    """
    for key, enum_class in key_enum_dict.items():
        if value := dato.get(key):
            dato[key] = enum_class(value)


def guardar_foto(instancia: models.Model, campo: str, nombre_foto: str, ruta_imagenes: Path):
    """Ayudante para guardar las fotos en los modelos del sistema

    Args:
        instancia (models.Model): Instancia de tipo django.db.models.Model
        campo (str): Nombre del campo
        nombre_foto (str): Nombre de la foto tal como esta guardada
        ruta_imagenes (Path): Ruta Global donde se encuentran las imagenes
    """
    if not nombre_foto:
        return

    ruta_foto = ruta_imagenes / nombre_foto

    if not ruta_foto.exists():
        return

    with ruta_foto.open("rb") as f:
        getattr(instancia, campo).save(
            ruta_foto.name,
            File(f),
            save=True,
        )


def parsear_fecha_aware(valor):
    """Convierte '2026-01-13' (o un datetime ISO) en un datetime *aware*.

    Devuelve None si `valor` está vacío o no se puede interpretar.
    """
    if not valor:
        return None
    fecha_hora = parse_datetime(valor)
    if fecha_hora is None:
        fecha = parse_date(valor)
        if fecha is None:
            return None
        fecha_hora = datetime.combine(fecha, time.min)
    if timezone.is_naive(fecha_hora):
        fecha_hora = timezone.make_aware(fecha_hora)
    return fecha_hora


def fijar_marcas_tiempo(instancia: models.Model, *, creado=None, actualizado=None):
    """Fija `creado`/`actualizado` a las fechas del JSON (la fecha en que se
    envió la solicitud / se registró el animal), en lugar de dejar el "ahora"
    que ponen los campos auto_now_add / auto_now.

    Se hace con QuerySet.update() porque save() ignora cualquier valor que se
    asigne a esos campos automáticos.
    """
    marcas = {}
    if (valor := parsear_fecha_aware(creado)) is not None:
        marcas["creado"] = valor
    if (valor := parsear_fecha_aware(actualizado)) is not None:
        marcas["actualizado"] = valor
    if marcas:
        type(instancia).objects.filter(pk=instancia.pk).update(**marcas)


class Command(BaseCommand):
    help = "Carga datos de ejemplo para demostrar el sistema (basados en casos reales)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--ruta-datos",
            type=Path,
            default=Path("core/fixtures/datos_happy_paws.json"),
            help="Ruta al archivo JSON de datos iniciales.",
        )
        parser.add_argument(
            "--ruta-imagenes",
            type=Path,
            default=Path("core/fixtures/HappyPaws"),
            help="Ruta a la carpeta de imágenes iniciales.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        ruta_datos: Path = options["ruta_datos"]
        ruta_imagenes: Path = options["ruta_imagenes"]

        self.stdout.write(f"Iniciando carga de datos desde: {ruta_datos.absolute()}")

        if not ruta_datos.exists():
            self.stdout.write(self.style.ERROR(f"El archivo {ruta_datos} no existe, abortando inicialización."))
            return
        if not ruta_imagenes.exists():
            self.stdout.write(
                self.style.ERROR(f"La carpeta de imágenes {ruta_imagenes} no existe, abortando inicialización.")
            )
            return

        with open(ruta_datos, "r", encoding="utf8") as json_file:
            datos_json = json.load(json_file)

        # --- Animales y Solicitudes de Adopción ---
        animales = datos_json.get("Animales", [])
        creados = {}
        n_solicitudes_adopcion = 0

        for animal_dato in animales:
            solicitudes_adopciones = animal_dato.pop("SolicitudesAdopciones", [])
            foto_principal = animal_dato.pop("foto_principal", None)
            # `creado`/`actualizado` no se pueden pasar en defaults (Django los
            # sobrescribe por auto_now_add / auto_now); se aplican aparte con
            # fijar_marcas_tiempo() para conservar la fecha real del JSON.
            marca_creado = animal_dato.pop("creado", None)
            marca_actualizado = animal_dato.pop("actualizado", None)
            convertir_key_a_enum(animal_dato, KEY2ENUM["Animales"])
            # update_or_create para que reimportar rellene/corrija filas ya
            # existentes; get_or_create ignora `defaults` cuando el animal ya existe.
            animal, creado = Animal.objects.update_or_create(
                nombre=animal_dato["nombre"],
                defaults={**animal_dato},
            )
            fijar_marcas_tiempo(animal, creado=marca_creado, actualizado=marca_actualizado)
            guardar_foto(animal, "foto_principal", foto_principal, ruta_imagenes)
            for solicitud in solicitudes_adopciones:
                marca_creado_solicitud = solicitud.pop("creado", None)
                convertir_key_a_enum(solicitud, KEY2ENUM["SolicitudesAdopciones"])
                solicitud_obj, app_creada = AdoptionApplication.objects.get_or_create(
                    animal=animal,
                    defaults={**solicitud},
                )
                fijar_marcas_tiempo(solicitud_obj, creado=marca_creado_solicitud)
                if app_creada:
                    n_solicitudes_adopcion += 1

            creados[animal_dato["nombre"]] = animal

        self.stdout.write(f"  · {len(animales)} animales procesados")
        self.stdout.write(f"  · {n_solicitudes_adopcion} nuevas solicitudes de adopción")

        # --- Casos Médicos ---
        casos_medicos = datos_json.get("Caso Médico", [])

        for caso_dato in casos_medicos:
            convertir_key_a_enum(caso_dato, KEY2ENUM["Caso Médico"])
            caso_data = caso_dato.copy()

            nombre_animal = caso_data.pop("nombre", None)
            datos_fotos_casos = caso_data.pop("fotos", [])

            animal = creados.get(nombre_animal)
            if not animal:
                continue

            donaciones = caso_data.pop("Donaciones", [])
            gastos = caso_data.pop("Gastos", [])
            avances = caso_data.pop("AvancesCasos", [])

            caso, creado = MedicalCase.objects.update_or_create(
                animal=animal,
                defaults=caso_data,
            )

            # Las colecciones anidadas (fotos, donaciones, gastos, avances) sólo
            # se siembran la primera vez; en reimportaciones basta con refrescar
            # los campos del caso.
            if not creado:
                continue

            for dato_foto_caso in datos_fotos_casos:
                foto_caso, foto_caso_creado = CasePhoto.objects.get_or_create(
                    caso=caso,
                    **dato_foto_caso,
                )
                if foto_caso_creado:
                    guardar_foto(
                        instancia=foto_caso,
                        campo="imagen",
                        nombre_foto=dato_foto_caso["imagen"],
                        ruta_imagenes=ruta_imagenes,
                    )

            # Donaciones
            for donacion_dato in donaciones:
                donacion_dato = donacion_dato.copy()
                donacion_dato.pop("comprobante", None)

                Donation.objects.create(
                    caso=caso,
                    **donacion_dato,
                )

            # Gastos
            for gasto_dato in gastos:
                convertir_key_a_enum(gasto_dato, KEY2ENUM["Gastos"])
                Expense.objects.create(
                    caso=caso,
                    **gasto_dato,
                )

            # Avances
            for avance_dato in avances:
                avance_dato = avance_dato.copy()
                nombre_foto_avance = avance_dato.pop("foto", None)

                avance, avance_creado = CaseUpdate.objects.get_or_create(
                    caso=caso,
                    **avance_dato,
                )

                if avance_creado and nombre_foto_avance:
                    guardar_foto(
                        instancia=avance,
                        campo="foto",
                        nombre_foto=nombre_foto_avance,
                        ruta_imagenes=ruta_imagenes,
                    )

        self.stdout.write(f"  · {len(casos_medicos)} casos médicos procesados")

        # --- Reportes ---
        reportes = datos_json.get("Reportes", [])
        n_comentario_reporte = 0
        n_avistamiento_reporte = 0

        for reporte_dato in reportes:
            imagen_avance = reporte_dato.pop("imagen", None)
            comentarios = reporte_dato.pop("Comentarios", [])
            avistamientos = reporte_dato.pop("Avistamientos", [])
            convertir_key_a_enum(reporte_dato, KEY2ENUM["Reportes"])
            reporte, creado = Report.objects.get_or_create(
                titulo=reporte_dato["titulo"],
                defaults={**reporte_dato},
            )

            if creado:
                for comentario in comentarios:
                    ReportComment.objects.create(reporte=reporte, **comentario)
                    n_comentario_reporte += 1

                for avistamiento in avistamientos:
                    ReportSighting.objects.create(reporte=reporte, **avistamiento)
                    n_avistamiento_reporte += 1

                if imagen_avance:
                    reporte_foto, _ = ReportPhoto.objects.get_or_create(reporte=reporte)
                    guardar_foto(reporte_foto, "imagen", imagen_avance, ruta_imagenes)
        self.stdout.write(f"  · {len(reportes)} reportes procesados")
        self.stdout.write(f"  · {n_comentario_reporte} comentarios y {n_avistamiento_reporte} avistamientos creados")

        self.stdout.write(self.style.SUCCESS("¡Datos de ejemplo cargados exitosamente!"))
