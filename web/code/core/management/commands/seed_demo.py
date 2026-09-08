import json
from pathlib import Path

from adoptions.models import AdoptionApplication
from animals.models import Animal
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from medical_cases.models import (
    CasePhoto,
    CaseUpdate,
    Donation,
    Expense,
    MedicalCase,
)
from reports.models import (
    Report,
    ReportComment,
    ReportPhoto,
    ReportSighting,
)

User = get_user_model()

# Campos que un animal necesita sí o sí para mostrarse completo en el panel.
# `edad_aprox` es opcional en el modelo (blank=True) pero lo pedimos igual
# porque el panel lo espera; si falta, sólo avisamos.
CAMPOS_OBLIGATORIOS_ANIMAL = ("nombre", "especie", "sexo", "tamano", "descripcion", "fecha_ingreso")
CAMPOS_RECOMENDADOS_ANIMAL = ("edad_aprox",)


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
        parser.add_argument(
            "--permitir-incompletos",
            action="store_true",
            help=(
                "No abortar si un animal del JSON no trae todos los campos "
                "obligatorios; sólo mostrar una advertencia."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        ruta_datos: Path = options["ruta_datos"]
        ruta_imagenes: Path = options["ruta_imagenes"]
        permitir_incompletos: bool = options["permitir_incompletos"]

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
        errores_datos = []

        for indice, data in enumerate(animales, start=1):
            solicitudes_adopciones = data.pop("SolicitudesAdopciones", [])
            nombre_foto = data.pop("foto_principal", None)
            ruta_foto = ruta_imagenes / nombre_foto if nombre_foto else None

            # `creado`/`actualizado` los gestiona Django (auto_now_add / auto_now);
            # si se pasan como texto rompen el guardado al reimportar (update).
            data.pop("creado", None)
            data.pop("actualizado", None)

            etiqueta = data.get("nombre") or f"#{indice}"

            faltantes = [c for c in CAMPOS_OBLIGATORIOS_ANIMAL if not data.get(c)]
            if faltantes:
                mensaje = f"Animal «{etiqueta}»: faltan campos obligatorios: {', '.join(faltantes)}"
                if permitir_incompletos:
                    self.stdout.write(self.style.WARNING(f"  ! {mensaje}"))
                else:
                    errores_datos.append(mensaje)
                    continue

            recomendados_faltantes = [c for c in CAMPOS_RECOMENDADOS_ANIMAL if not data.get(c)]
            if recomendados_faltantes:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ! Animal «{etiqueta}»: sin {', '.join(recomendados_faltantes)} "
                        f"(el panel lo mostrará vacío)"
                    )
                )

            # update_or_create para que reimportar repare filas ya cargadas
            # (get_or_create ignora `defaults` cuando el animal ya existe).
            animal, creado = Animal.objects.update_or_create(
                nombre=data["nombre"],
                defaults={**data},
            )

            if ruta_foto and ruta_foto.exists() and not animal.foto_principal:
                with open(ruta_foto, "rb") as f:
                    animal.foto_principal.save(ruta_foto.name, File(f), save=True)

            for solicitud in solicitudes_adopciones:
                solicitud.pop("creado", None)  # lo gestiona Django (auto_now_add)
                _, app_creada = AdoptionApplication.objects.get_or_create(
                    animal=animal,
                    nombre_solicitante=solicitud.get("nombre_solicitante", ""),
                    defaults={**solicitud},
                )
                if app_creada:
                    n_solicitudes_adopcion += 1

            creados[data["nombre"]] = animal

        if errores_datos:
            raise CommandError(
                "El JSON de datos tiene animales incompletos; se cancela la carga "
                "(usa --permitir-incompletos para forzarla):\n  - " + "\n  - ".join(errores_datos)
            )

        self.stdout.write(f"  · {len(animales)} animales procesados")
        self.stdout.write(f"  · {n_solicitudes_adopcion} nuevas solicitudes de adopción")

        # --- Casos Médicos ---
        casos_medicos = datos_json.get("Caso Médico", [])
        for caso_dato in casos_medicos:
            nombre_animal = caso_dato.pop("nombre")
            nombre_foto = caso_dato.pop("foto", None)
            ruta_foto = ruta_imagenes / nombre_foto if nombre_foto else None

            animal = creados.get(nombre_animal)
            if not animal:
                continue

            # Colecciones anidadas: se sacan de `caso_dato` para que sólo queden
            # campos propios de MedicalCase (si no, `update_or_create` lanza
            # FieldError por claves como 'fotos' o 'AvancesCasos').
            donaciones = caso_dato.pop("Donaciones", [])
            gastos = caso_dato.pop("Gastos", [])
            fotos_caso = caso_dato.pop("fotos", [])
            avances_caso = caso_dato.pop("AvancesCasos", [])

            caso, creado = MedicalCase.objects.update_or_create(
                animal=animal,
                defaults={**caso_dato},
            )

            if ruta_foto and ruta_foto.exists() and not caso.foto:
                with open(ruta_foto, "rb") as f:
                    caso.foto.save(ruta_foto.name, File(f), save=True)

            if creado:
                for donacion in donaciones:
                    donacion.pop("comprobante", None)
                    donacion.pop("creado", None)  # auto_now_add
                    Donation.objects.create(caso=caso, **donacion)
                for gasto in gastos:
                    gasto.pop("comprobante", None)
                    gasto.pop("creado", None)  # auto_now_add
                    Expense.objects.create(caso=caso, **gasto)
                for foto in fotos_caso:
                    # La imagen se referencia por ruta; sólo guardamos la descripción.
                    foto.pop("imagen", None)
                    CasePhoto.objects.create(caso=caso, **foto)
                for avance in avances_caso:
                    avance.pop("foto", None)
                    CaseUpdate.objects.create(caso=caso, **avance)

        self.stdout.write(f"  · {len(casos_medicos)} casos médicos procesados")

        # --- Reportes ---
        reportes = datos_json.get("Reportes", [])
        n_comentario_reporte = 0
        n_avistamiento_reporte = 0

        for reporte_datos in reportes:
            nombre_foto = reporte_datos.pop("imagen", None)
            ruta_foto = ruta_imagenes / nombre_foto if nombre_foto else None
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

                if ruta_foto and ruta_foto.exists():
                    reporte_foto, _ = ReportPhoto.objects.get_or_create(reporte=reporte)
                    with open(ruta_foto, "rb") as f:
                        reporte_foto.imagen.save(ruta_foto.name, File(f), save=True)

        self.stdout.write(f"  · {len(reportes)} reportes procesados")
        self.stdout.write(f"  · {n_comentario_reporte} comentarios y {n_avistamiento_reporte} avistamientos creados")

        self.stdout.write(self.style.SUCCESS("¡Datos de ejemplo cargados exitosamente!"))
