import json
from pathlib import Path

from adoptions.models import AdoptionApplication
from animals.models import Animal
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from medical_cases.models import CaseUpdate, Donation, Expense, MedicalCase
from reports.models import (
    Report,
    ReportComment,
    ReportPhoto,
    ReportSighting,
)

User = get_user_model()


def guardar_foto(instancia, campo, nombre_foto, ruta_imagenes):
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

        for data in animales:
            solicitudes_adopciones = data.pop("SolicitudesAdopciones", [])
            nombre_foto = data.pop("foto_principal", None)
            ruta_foto = ruta_imagenes / nombre_foto if nombre_foto else None

            animal, creado = Animal.objects.get_or_create(
                nombre=data["nombre"],
                defaults={**data},
            )

            if creado and ruta_foto and ruta_foto.exists():
                with open(ruta_foto, "rb") as f:
                    animal.foto_principal.save(ruta_foto.name, File(f), save=True)

            for solicitud in solicitudes_adopciones:
                _, app_creada = AdoptionApplication.objects.get_or_create(
                    animal=animal,
                    defaults={**solicitud},
                )
                if app_creada:
                    n_solicitudes_adopcion += 1

            creados[data["nombre"]] = animal

        self.stdout.write(f"  · {len(animales)} animales procesados")
        self.stdout.write(f"  · {n_solicitudes_adopcion} nuevas solicitudes de adopción")

        # --- Casos Médicos ---
        casos_medicos = datos_json.get("Caso Médico", [])

        for caso_dato in casos_medicos:
            caso_data = caso_dato.copy()

            nombre_animal = caso_data.pop("nombre", None)
            nombre_foto = caso_data.pop("foto", None)

            animal = creados.get(nombre_animal)
            if not animal:
                continue

            donaciones = caso_data.pop("Donaciones", [])
            gastos = caso_data.pop("Gastos", [])
            avances = caso_data.pop("AvancesCasos", [])

            caso, creado = MedicalCase.objects.get_or_create(
                animal=animal,
                defaults=caso_data,
            )

            if not creado:
                continue

            # Foto principal
            guardar_foto(
                instancia=caso,
                campo="foto",
                nombre_foto=nombre_foto,
                ruta_imagenes=ruta_imagenes,
            )

            # Donaciones
            for donacion_data in donaciones:
                donacion_data = donacion_data.copy()
                donacion_data.pop("comprobante", None)

                Donation.objects.create(
                    caso=caso,
                    **donacion_data,
                )

            # Gastos
            for gasto_data in gastos:
                Expense.objects.create(
                    caso=caso,
                    **gasto_data,
                )

            # Avances
            for avance_data in avances:
                avance_data = avance_data.copy()
                nombre_foto_avance = avance_data.pop("foto", None)

                avance, avance_creado = CaseUpdate.objects.get_or_create(
                    caso=caso,
                    **avance_data,
                )

                if avance_creado:
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

        for reporte_datos in reportes:
            nombre_foto = reporte_datos.pop("imagen", None)
            ruta_foto_avance = ruta_imagenes / nombre_foto if nombre_foto else None
            comentarios = reporte_datos.pop("Comentarios", [])
            avistamientos = reporte_datos.pop("Avistamientos", [])

            reporte, creado = Report.objects.get_or_create(
                titulo=reporte_datos["titulo"],
                defaults={**reporte_datos},
            )

            if creado:
                for comentario in comentarios:
                    ReportComment.objects.create(reporte=reporte, **comentario)
                    n_comentario_reporte += 1

                for avistamiento in avistamientos:
                    ReportSighting.objects.create(reporte=reporte, **avistamiento)
                    n_avistamiento_reporte += 1

                if ruta_foto_avance and ruta_foto_avance.exists():
                    reporte_foto, _ = ReportPhoto.objects.get_or_create(reporte=reporte)
                    with open(ruta_foto_avance, "rb") as f:
                        reporte_foto.imagen.save(ruta_foto_avance.name, File(f), save=True)

        self.stdout.write(f"  · {len(reportes)} reportes procesados")
        self.stdout.write(f"  · {n_comentario_reporte} comentarios y {n_avistamiento_reporte} avistamientos creados")

        self.stdout.write(self.style.SUCCESS("¡Datos de ejemplo cargados exitosamente!"))
