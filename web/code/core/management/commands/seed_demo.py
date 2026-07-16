from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from adoptions.models import AdoptionApplication, EstadoSolicitud, TipoVivienda
from animals.models import Animal, EstadoAnimal, Especie, Sexo, Tamano
from medical_cases.models import CaseUpdate, Donation, EstadoCaso, MedicalCase
from reports.models import (
    EstadoReporte,
    Report,
    ReportComment,
    ReportSighting,
    TipoReporte,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Carga datos de ejemplo para demostrar el sistema (basados en casos reales)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Cargando datos de ejemplo…")

        # --- Usuario staff de la fundación ---
        if not User.objects.filter(username="fundacion").exists():
            User.objects.create_user(
                username="fundacion",
                password="happypaws123",
                first_name="Equipo",
                last_name="Happy Paws",
                email="happypaws.pillaro@gmail.com",
                is_staff=True,
            )
            self.stdout.write("  · Usuario staff: fundacion / happypaws123")

        # --- Animales ---
        hoy = date.today()
        animales = [
            {
                "nombre": "Lulu", "especie": Especie.PERRO, "sexo": Sexo.HEMBRA,
                "tamano": Tamano.MEDIANO, "edad_aprox": "2 años",
                "estado": EstadoAnimal.EN_TRATAMIENTO, "esterilizado": False,
                "descripcion": "Encontrada gravemente herida en su rostro, "
                               "probablemente atropellada. En recuperación tras cirugía.",
            },
            {
                "nombre": "Canela", "especie": Especie.PERRO, "sexo": Sexo.HEMBRA,
                "tamano": Tamano.MEDIANO, "edad_aprox": "1 año",
                "estado": EstadoAnimal.EN_ADOPCION, "esterilizado": True,
                "descripcion": "Perrita rescatada del parque de Píllaro. Cariñosa, "
                               "sociable y lista para una familia responsable.",
            },
            {
                "nombre": "Manchas", "especie": Especie.GATO, "sexo": Sexo.MACHO,
                "tamano": Tamano.PEQUENO, "edad_aprox": "6 meses",
                "estado": EstadoAnimal.EN_ADOPCION, "esterilizado": True,
                "descripcion": "Gatito juguetón rescatado de la calle. Sano y desparasitado.",
            },
            {
                "nombre": "Rocky", "especie": Especie.PERRO, "sexo": Sexo.MACHO,
                "tamano": Tamano.GRANDE, "edad_aprox": "3 años",
                "estado": EstadoAnimal.EN_ADOPCION, "esterilizado": True,
                "descripcion": "Perro grande, tranquilo y leal. Ideal para casa con patio.",
            },
            {
                "nombre": "Nube", "especie": Especie.GATO, "sexo": Sexo.HEMBRA,
                "tamano": Tamano.PEQUENO, "edad_aprox": "2 años",
                "estado": EstadoAnimal.ADOPTADO, "esterilizado": True,
                "descripcion": "Gatita blanca adoptada por una familia de Píllaro.",
            },
            {
                "nombre": "Toby", "especie": Especie.PERRO, "sexo": Sexo.MACHO,
                "tamano": Tamano.PEQUENO, "edad_aprox": "8 meses",
                "estado": EstadoAnimal.HOGAR_TEMPORAL, "esterilizado": False,
                "descripcion": "Cachorro en hogar temporal mientras completa sus vacunas.",
            },
        ]
        creados = {}
        for data in animales:
            animal, _ = Animal.objects.get_or_create(
                nombre=data["nombre"],
                defaults={**data, "fecha_ingreso": hoy - timedelta(days=30)},
            )
            creados[data["nombre"]] = animal
        self.stdout.write(f"  · {len(animales)} animales")

        # --- Caso médico (Ojito Lulu) ---
        caso, nuevo = MedicalCase.objects.get_or_create(
            titulo="Caso Ojito Lulu",
            defaults={
                "animal": creados["Lulu"],
                "descripcion": "Lulu perdió un ojito y tiene una lesión en la mandíbula. "
                               "Necesitamos cubrir el costo de su cirugía y medicación.",
                "meta_monto": Decimal("121.00"),
                "estado": EstadoCaso.ACTIVO,
            },
        )
        if nuevo:
            Donation.objects.create(
                caso=caso, nombre_donante="Ana Gómez", monto=Decimal("50.00"),
                fecha=hoy - timedelta(days=5), verificado=True,
            )
            Donation.objects.create(
                caso=caso, nombre_donante="Carlos Ruiz", monto=Decimal("46.00"),
                fecha=hoy - timedelta(days=3), verificado=True,
            )
            Donation.objects.create(
                caso=caso, nombre_donante="Donante anónimo", monto=Decimal("20.00"),
                fecha=hoy - timedelta(days=1), verificado=False,
            )
            CaseUpdate.objects.create(
                caso=caso, fecha=hoy - timedelta(days=2),
                texto="Lulu salió de cirugía y se está recuperando. ¡Gracias por su apoyo!",
            )
        self.stdout.write("  · 1 caso médico con donaciones y avances")

        # --- Reportes ---
        reportes = [
            {
                "tipo": TipoReporte.PERDIDO, "titulo": "Perrito blanco con ojos azules",
                "ubicacion": "Sector de Chagrapamba, Píllaro",
                "descripcion": "Perrito visto durante los últimos días en el sector. "
                               "Si conoces a sus dueños, ayúdanos a contactarlos.",
            },
            {
                "tipo": TipoReporte.PERDIDO, "titulo": "Zeus y Hércules - se perdieron juntos",
                "ubicacion": "Sector del Hospital Municipal, Tungurahua",
                "descripcion": "Dos perros (uno blanco, otro café con blanco) perdidos. "
                               "Ambos necesitan sus medicamentos.",
            },
            {
                "tipo": TipoReporte.ENCONTRADO, "titulo": "Perrita encontrada en el Parque de Píllaro",
                "ubicacion": "Parque central de Píllaro",
                "descripcion": "Perrita al parecer extraviada de su casa. Está a salvo, "
                               "buscamos a su familia.",
            },
            {
                "tipo": TipoReporte.MALTRATO, "titulo": "Abandono de cachorros en Ciudad Nueva",
                "ubicacion": "Callejón de las Calles Vía a la Primavera, Píllaro",
                "descripcion": "Se reporta el abandono de dos cachorros. Buscamos evidencia "
                               "para identificar al responsable según la ordenanza municipal.",
                "estado": EstadoReporte.RESUELTO,
            },
        ]
        reportes_creados = {}
        for data in reportes:
            reporte, _ = Report.objects.get_or_create(
                titulo=data["titulo"],
                defaults={
                    **data,
                    "fecha_avistamiento": hoy - timedelta(days=4),
                    "nombre_reportante": "Vecino de Píllaro",
                    "contacto_reportante": "099 906 3323",
                    "aprobado": True,
                },
            )
            reportes_creados[data["titulo"]] = reporte
        self.stdout.write(f"  · {len(reportes)} reportes")

        # --- Interacción comunitaria de ejemplo ---
        perdido = reportes_creados["Perrito blanco con ojos azules"]
        if not perdido.comentarios.exists():
            ReportComment.objects.create(
                reporte=perdido, nombre="Marta",
                mensaje="Creo que lo vi cerca del mercado esta mañana, andaba asustado.",
            )
            ReportComment.objects.create(
                reporte=perdido, nombre="Don José", contacto="098 765 4321",
                mensaje="Yo le di agua ayer en la tarde, sigue por el sector.",
            )
        if not perdido.avistamientos.exists():
            ReportSighting.objects.create(
                reporte=perdido, nombre="Marta", contacto="0991234567",
                ubicacion="Mercado Central de Píllaro", fecha=hoy - timedelta(days=1),
                descripcion="Estaba junto a los puestos de fruta, se fue hacia el parque.",
                confirmado=True,
            )
            ReportSighting.objects.create(
                reporte=perdido, nombre="Carlos",
                ubicacion="Parque de Píllaro", fecha=hoy,
                descripcion="Lo vi cruzar hacia la iglesia.",
            )
        self.stdout.write("  · comentarios y avistamientos de ejemplo")

        # --- Solicitud de adopción de ejemplo ---
        AdoptionApplication.objects.get_or_create(
            animal=creados["Canela"],
            cedula="1804567890",
            defaults={
                "nombre_solicitante": "María Pérez",
                "telefono": "0991234567",
                "email": "maria.perez@example.com",
                "direccion": "Av. Rumiñahui 123, Píllaro",
                "tipo_vivienda": TipoVivienda.CASA,
                "tiene_patio": True,
                "experiencia": "He tenido perros toda mi vida.",
                "estado": EstadoSolicitud.PENDIENTE,
            },
        )
        self.stdout.write("  · 1 solicitud de adopción")

        self.stdout.write(self.style.SUCCESS("¡Datos de ejemplo cargados!"))
