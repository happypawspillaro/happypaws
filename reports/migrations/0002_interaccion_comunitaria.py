# Interacción comunitaria: comentarios y avistamientos en los reportes.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, verbose_name="tu nombre")),
                ("contacto", models.CharField(blank=True, help_text="Teléfono o correo, por si quieren responderte.", max_length=200, verbose_name="contacto (opcional)")),
                ("mensaje", models.TextField(verbose_name="mensaje")),
                ("oculto", models.BooleanField(default=False, verbose_name="oculto por moderación")),
                ("creado", models.DateTimeField(auto_now_add=True)),
                ("reporte", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comentarios", to="reports.report")),
            ],
            options={
                "verbose_name": "comentario",
                "verbose_name_plural": "comentarios",
                "ordering": ["creado"],
            },
        ),
        migrations.CreateModel(
            name="ReportSighting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, verbose_name="tu nombre")),
                ("contacto", models.CharField(blank=True, help_text="Teléfono o correo, por si el dueño necesita más detalles.", max_length=200, verbose_name="contacto (opcional)")),
                ("ubicacion", models.CharField(max_length=255, verbose_name="¿dónde lo viste?")),
                ("fecha", models.DateField(verbose_name="¿cuándo lo viste?")),
                ("descripcion", models.TextField(blank=True, verbose_name="detalles")),
                ("foto", models.ImageField(blank=True, upload_to="reportes/avistamientos/", verbose_name="foto (opcional)")),
                ("confirmado", models.BooleanField(default=False, verbose_name="confirmado por la fundación")),
                ("oculto", models.BooleanField(default=False, verbose_name="oculto por moderación")),
                ("creado", models.DateTimeField(auto_now_add=True)),
                ("reporte", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="avistamientos", to="reports.report")),
            ],
            options={
                "verbose_name": "avistamiento",
                "verbose_name_plural": "avistamientos",
                "ordering": ["-creado"],
            },
        ),
    ]
