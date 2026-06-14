# Hoja de ruta — Happy Paws Píllaro

> Sistema web integral de gestión para la fundación de protección animal Happy Paws (Píllaro, Tungurahua, Ecuador).
> Documento de planificación técnica. Complementa al Plan de Proyecto FR05.
>
> **Última actualización:** 1 de junio de 2026 · **Fecha tope de tesis:** 14 de agosto de 2026

---

## 1. Visión del producto

Happy Paws centraliza en una sola plataforma lo que hoy la fundación maneja disperso en redes
sociales y hojas de cálculo, **complementando** (no reemplazando) al sistema **Esterilizaya** que
ya gestiona las jornadas de esterilización.

El objetivo de fondo es cerrar el ciclo completo de bienestar animal:

```
  Esterilizaya            HAPPY PAWS (este sistema)
 ┌───────────┐    ┌──────────────────────────────────────────────┐
 │ Jornada   │    │  Catálogo → Adopción → Seguimiento            │
 │ de        │───▶│  Caso médico → Recaudación → Avances          │
 │ esteril.  │    │  Reporte comunitario → Pistas → Resolución    │
 └───────────┘    │  Panel staff + Transparencia pública          │
                  └──────────────────────────────────────────────┘
   esterilizado        rescatado → en adopción → adoptado
```

**Principio rector:** cada animal esterilizado en una jornada puede convertirse en un animal
publicado en el catálogo de adopción → el sistema vuelve *medible* el impacto de la fundación.

---

## 2. Estado actual — Fase 0 ✅ (completada)

El MVP ya cubre el núcleo operativo. Módulos en producción funcional:

| Módulo | Qué hace hoy | Estado |
|--------|--------------|--------|
| **Animales** | Catálogo con filtros (especie/sexo/tamaño) vía HTMX, fichas, fotos, historial médico, CRUD staff | ✅ |
| **Adopciones** | Solicitud pública por animal, seguimiento post-adopción, gestión y cambio de estado | ✅ |
| **Casos médicos** | Recaudación con barra de progreso, donaciones verificables, bitácora de avances | ✅ |
| **Reportes comunitarios** | Perdido/encontrado/maltrato + comentarios y avistamientos públicos, notificación por correo, moderación staff, honeypot anti-spam | ✅ |
| **Cuentas** | Auth, registro, usuario custom con teléfono, decorador `staff_required` | ✅ |
| **Core** | Home con destacados, dashboard de métricas para staff, comando `seed_demo` | ✅ |

**Stack:** Django 5.1 · HTMX 2 · Bootstrap 5 · SQLite/PostgreSQL · desplegable gratis en PythonAnywhere.

**Calidad:** suite de tests en `reports/` (honeypot, moderación, permisos, notificaciones). Pendiente extenderla al resto de módulos.

---

## 3. Mapeo a los objetivos de la tesis (FR05)

Cada fase de la hoja de ruta sustenta un objetivo específico del proyecto. La **deficiencia**
que se resuelve: la fundación tiene un sistema parcial (Esterilizaya) e información dispersa, sin
una plataforma integral que conecte esterilización, adopción, casos médicos y participación
comunitaria, ni que muestre su impacto de forma transparente.

| Objetivo específico (tesis) | Fase que lo evidencia |
|-----------------------------|-----------------------|
| Centralizar la gestión de animales y adopciones | Fase 0 ✅ |
| Habilitar la participación de la comunidad | Fase 0 ✅ (reportes + interacción) |
| **Integrar con el sistema Esterilizaya existente** | **Fase 1** |
| **Transparentar el impacto ante la comunidad y donantes** | **Fase 2** |
| Asegurar calidad, despliegue y sostenibilidad del sistema | Fase 3 |

---

## 4. Hoja de ruta por fases

### 🟦 Fase 1 — Integración con Esterilizaya `(jun 2026)`
*Objetivo de tesis: demostrar que el nuevo sistema complementa e integra al existente.*

El argumento más fuerte de la tesis: ya existe un sistema parcial, y este lo vuelve integral
cerrando el ciclo **esterilización → adopción**.

- [ ] Definir el mecanismo de integración real con Esterilizaya (a confirmar según su tecnología):
  - **Opción A — Importación**: comando de carga (CSV/Excel export de Esterilizaya → animales).
  - **Opción B — API/lectura BD**: si Esterilizaya expone datos, sincronización programada.
  - **Opción C — Registro manual asistido**: formulario staff que marca origen "jornada de esterilización".
- [ ] Modelo: añadir trazabilidad de origen en `Animal` (campo `origen` / `jornada_esterilizacion`, fecha, reutilizar `esterilizado`).
- [ ] Flujo: animal esterilizado en jornada → ficha precargada → publicar en catálogo en un clic.
- [ ] Métrica nueva en dashboard: "animales provenientes de jornadas que fueron adoptados".
- [ ] Documentar la integración en la tesis (diagrama de arquitectura del ecosistema).

> **Decisión pendiente:** confirmar contigo la tecnología/acceso de Esterilizaya para elegir A/B/C.

### 🟩 Fase 2 — Transparencia pública `(jul 2026)`
*Objetivo de tesis: el sistema rinde cuentas a la comunidad y a los donantes.*

Hoy las métricas solo las ve el staff. Esta fase las saca a la luz y genera confianza/donaciones.

- [ ] Página pública **"Nuestro impacto"** (`/impacto/`) con cifras agregadas:
  - Animales rescatados / en adopción / adoptados.
  - Total recaudado y nº de casos médicos resueltos.
  - Animales esterilizados (dato puente con Esterilizaya).
  - Reportes comunitarios resueltos.
- [ ] Contadores en vivo y gráficos simples (sin librerías pesadas; Bootstrap + SVG o Chart.js mínimo).
- [ ] Transparencia por caso: en cada caso médico, donaciones verificadas visibles (monto, sin datos personales).
- [ ] "Historias de éxito": animales adoptados destacados con su antes/después.
- [ ] Exportable: reporte PDF de impacto (mensual/anual) para la fundación.

### 🟨 Fase 3 — Calidad, despliegue y cierre de tesis `(jul–ago 2026)`
*Objetivo de tesis: sistema sostenible, probado y desplegado.*

- [ ] Extender suite de tests a `animals`, `adoptions`, `medical_cases`, `accounts`.
- [ ] Validaciones de formularios y manejo de errores consistente.
- [ ] Accesibilidad y responsive (revisión móvil — la comunidad entra por celular).
- [ ] Despliegue estable en PythonAnywhere con datos reales de la fundación.
- [ ] Manual de usuario (staff) y de administrador.
- [ ] Cierre documental: capturas, diagramas, resultados para la defensa.
- [ ] **Corte 14/08/2026** — todo lo anterior cerrado para la entrega.

---

## 5. Visión a futuro (post-tesis / backlog)

Ideas que exceden el alcance de la tesis pero marcan el norte del producto. No son compromisos
de fecha; son el "qué más se le puede añadir".

### 🗺️ Geolocalización
- Mapa interactivo para reportes y avistamientos (perdidos/encontrados) — hoy la ubicación es texto libre.
- "Mascotas perdidas cerca de ti" por zona de Píllaro/Tungurahua.

### 📱 Canal de notificación real (WhatsApp)
- En Ecuador el canal real de las fundaciones es WhatsApp, no el correo.
- Notificar avistamientos y cambios de estado por WhatsApp/SMS además del email.
- Botón "compartir en WhatsApp" en fichas de adopción y casos médicos.

### 🙋 Voluntariado y hogares temporales
- El estado "hogar temporal" ya existe en `Animal` pero no hay flujo para postularse.
- Registro de voluntarios, hogares de paso y padrinos/madrinas de animales.

### 💳 Donaciones en línea
- Integración con pasarela de pago local (PayPhone, Datafast, transferencia con comprobante automatizado).
- Recibos automáticos y conciliación de donaciones.

### 📊 Inteligencia de gestión
- Reportería avanzada y tendencias (adopciones por mes, especies más rescatadas, zonas con más reportes).
- Recordatorios automáticos de seguimiento post-adopción y de vacunación/desparasitación.

### 🤝 Ecosistema
- API pública para que veterinarias aliadas consulten/publiquen casos.
- Vinculación con redes sociales (publicación automática de animales nuevos).

---

## 6. Resumen visual de fases

```
  HOY (1 jun)                                          TESIS (14 ago)
     │                                                       │
     ▼                                                       ▼
  ┌──────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
  │Fase 0│──▶│   Fase 1    │──▶│   Fase 2     │──▶│     Fase 3       │
  │ MVP  │   │ Esterilizaya│   │Transparencia │   │ Calidad+Deploy   │
  │  ✅  │   │ integración │   │   pública    │   │  + cierre tesis  │
  └──────┘   └─────────────┘   └──────────────┘   └──────────────────┘
              objetivo:         objetivo:           objetivo:
              "complementa      "rinde cuentas"     "sostenible y
               lo existente"                         probado"

  ───────────────── POST-TESIS (backlog) ─────────────────────────────
   Mapas · WhatsApp · Voluntariado · Pagos en línea · Reportería · API
```

---

## 7. Cómo colaborar con esta hoja de ruta

- Cada `[ ]` es una tarea accionable; se marcan al completarse.
- Las **decisiones pendientes** (ej. tecnología de Esterilizaya) están señaladas y requieren tu input.
- Las fases 1–3 caben dentro del plazo de tesis; el backlog es opcional/futuro.
- Se sugiere una rama por fase: `feature/integracion-esterilizaya`, `feature/transparencia-publica`, etc.
