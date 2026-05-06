# MetroHub

Plataforma web de programación inteligente de horarios y asignación de choferes para el Metropolitano de Lima

> Proyecto universitario — Universidad Nacional de Ingeniería  
> Facultad de Ciencias · Escuela Profesional de Ciencia de la Computación  
> Versión 1.0 · Abril 2026

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Equipo](#equipo)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Requisitos funcionales](#requisitos-funcionales)
- [Requisitos no funcionales](#requisitos-no-funcionales)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Uso del sistema](#uso-del-sistema)
- [Gestión del proyecto — Scrum](#gestión-del-proyecto--scrum)
- [Estado actual del sprint](#estado-actual-del-sprint)

---

## Descripción general

MetroHub es una aplicación web de uso **interno y restringido** diseñada para la Autoridad de Transporte Urbano (ATU) de Lima. Reemplaza el flujo manual basado en hojas de cálculo con el que actualmente la ATU y los concesionarios programan los horarios del Metropolitano y asignan choferes por ruta y turno.

El sistema **no está orientado al pasajero final** y no expone funcionalidades públicas. El acceso está restringido a redes internas autorizadas o VPN.

### Usuarios del sistema

| Perfil | Descripción |
|--------|-------------|
| **Administrador ATU** | Accede con credenciales institucionales. Configura rutas y estaciones, aprueba programaciones, gestiona concesionarios, visualiza KPIs globales y genera reportes oficiales. Acceso total. |
| **Supervisor de Concesionario** | Registra y actualiza la disponibilidad de choferes y unidades de su empresa. Visualiza la programación aprobada de su concesionario. Acceso limitado a sus propios datos. |

---

## Equipo

| Integrante | Código | Rol |
|------------|--------|-----|
| Erick Daniel Ortega Moran | 20210209H | Líder / Business Analyst — Requisitos, frontend, gestión de backlog |
| Cesar Abrahan Correa Mullisaca | 20220305J | Dev — Backend y fusión frontend-backend |
| Isaac Antonio Martel Balvin | 20231462D | Dev — Backend e integración del sistema |
| Diego Torres Picho | 20204113B | Creacion de DB, QA — Datos de prueba y testing manual |
| Ivett Marinella Mera Amado | 20191471H | QA — Investigación de datos del Metropolitano y testing |

Docente: Prof. Manuel Quispe Torres

---

## Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 19 | Framework UI (SPA) |
| Vite | 8 | Bundler y dev server |
| Fetch API (`api.js`) | nativa | Cliente HTTP centralizado con inyección JWT |
| DM Sans + Space Mono | — | Tipografía del sistema |

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.111+ | API REST |
| SQLAlchemy | 2.0 | ORM conectado a PostgreSQL |
| python-jose | 3.3+ | Autenticación JWT y sesiones |
| passlib + bcrypt | 1.7+ | Hash de contraseñas (factor >= 12) |
| Alembic | 1.13+ | Migraciones de base de datos |

### Base de datos y caché
| Tecnología | Versión | Uso |
|------------|---------|-----|
| PostgreSQL | 16 | Base de datos principal |
| Redis | 7+ | Caché de consultas frecuentes |

### Módulo IA *(pendiente — Sprint 2)*
| Tecnología | Uso |
|------------|-----|
| OR-Tools / PuLP | Optimización de asignación de choferes (programación lineal entera) |
| Prophet | Predicción de demanda por ruta, hora y día de la semana |

### DevOps
| Tecnología | Uso |
|------------|-----|
| Docker + Docker Compose | 4 contenedores: backend, frontend, db, redis |
| GitHub | Control de versiones y gestión de ramas |
| Jira (Scrum) | Gestión de sprints y backlog |

---

## Arquitectura

El sistema se organiza en tres capas:

```
Capa de Presentación
├── React 19 SPA (uso interno — red ATU o VPN)
├── Panel Administrador ATU
└── Panel Supervisor de Concesionario

        HTTPS / API REST

Capa de Negocio
├── FastAPI (patrón MVC)
├── Routers: auth, rutas, horarios, choferes, dashboard, conflictos
├── Services: lógica de negocio y queries SQLAlchemy
└── Autenticación JWT + control de roles

        Conexiones internas

Capa de Datos e Inteligencia Artificial
├── PostgreSQL 16 (11 tablas, triggers, vista v_dashboard_kpis)
├── OR-Tools (optimización de asignación — pendiente)
├── Prophet (predicción de demanda — pendiente)
└── Redis (caché)
```

### Patrón de Monorepo

Frontend y Backend coexisten en el mismo repositorio, permitiendo:
- Desarrollo paralelo sincronizado
- Testing de integración simplificado
- Deploy coordinado mediante Docker Compose
- Versionado compartido

---

## Requisitos funcionales

### RF01 — Autenticación y Control de Roles
- Login con correo institucional y contraseña
- Hash bcrypt con factor >= 12
- Sesión con token JWT, expira a las 8 horas de inactividad
- Bloqueo de cuenta tras 5 intentos fallidos consecutivos
- Administrador ATU: acceso total al sistema
- Supervisor de Concesionario: acceso restringido a su concesionario

### RF02 — Gestión de Rutas y Estaciones
- CRUD completo de rutas: código, nombre, estaciones, paraderos, frecuencia base y concesionario asignado
- CRUD de estaciones: ubicación geográfica (GPS), capacidad operativa, horarios por día de semana
- Activar y desactivar rutas
- Los cambios impactan inmediatamente en el módulo de programación

### RF03 — Programación de Horarios
- Grilla visual interactiva de horarios por ruta y rango de fechas
- Validación en tiempo real: solapamiento de turnos, disponibilidad del chofer, horas máximas (8 h)
- Resolución interactiva de conflictos desde la UI (solo Administrador ATU)
- Publicación de programación aprobada visible para los Supervisores del concesionario correspondiente

### RF04 — Gestión de Choferes y Asignación
- Registro de choferes con datos personales, licencia tipo A-III y certificación Protransporte
- Asignación a turnos y rutas con control de horas máximas (8 h/jornada)
- Alertas automáticas de documentos por vencer (licencia y certificación Protransporte)
- Control de disponibilidad: activo, vacaciones, licencia médica, suspendido, inactivo

### RF05 — Optimización con IA *(pendiente — Sprint 2)*
- Predicción de demanda por ruta, hora y día con modelo Prophet
- Optimización de asignación de choferes y buses con OR-Tools
- Propuesta automática revisable y aprobable por el Administrador ATU

### RF06 — Dashboard de Indicadores y Reportes
- KPIs operativos actualizados desde la BD: rutas activas, choferes disponibles, buses operativos, conflictos pendientes, certificaciones por vencer en 30 días
- Exportación de reportes en PDF y XLSX *(pendiente — Sprint 2)*

---

## Requisitos no funcionales

| ID | Nombre | Descripción clave |
|----|--------|-------------------|
| RNF01 | Usabilidad | Programación semanal en <= 15 min. Dashboard <= 2 niveles de menú. WCAG 2.1 AA. |
| RNF02 | Seguridad | HTTPS (TLS 1.2+), bcrypt >= 12, OWASP Top 10, aislamiento por concesionario, Ley 29733. |
| RNF03 | Desempeño | API REST <= 2 s (p95). Validación de conflictos <= 1 s. Propuesta IA <= 30 s. 100 usuarios concurrentes. |
| RNF04 | Disponibilidad | 99% uptime horario operativo (07:00-19:00, lun-sáb). RTO <= 30 min. Funcional sin módulo IA. |
| RNF05 | Mantenibilidad | >= 70% cobertura en módulos críticos. PEP 8 (backend), ESLint (frontend). Arquitectura MVC modular. |
| RNF06 | Portabilidad | Chrome 90+, Firefox 88+, Edge 90+. Responsivo 768px-1920px. Backend en Docker. |

---

## Estructura del proyecto

```
MetroHub/
├── frontend/                      # React 19 + Vite 8
│   ├── public/
│   ├── src/
│   │   ├── api.js                # Cliente HTTP centralizado (Fetch + JWT)
│   │   ├── components/
│   │   │   ├── Sidebar.jsx       # Menú lateral de navegación
│   │   │   ├── KpiCard.jsx       # Tarjeta de indicador KPI
│   │   │   ├── RouteBar.jsx      # Barra de cobertura por ruta
│   │   │   └── AlertPanel.jsx    # Panel de alertas activas
│   │   ├── pages/
│   │   │   ├── Login.jsx         # RF01 — Autenticación contra API
│   │   │   ├── Dashboard.jsx     # RF06 — KPIs desde PostgreSQL
│   │   │   ├── Grilla.jsx        # RF03 — Horarios + resolución de conflictos
│   │   │   ├── Rutas.jsx         # RF02 — Catálogo de rutas desde BD
│   │   │   └── Choferes.jsx      # RF04 — Choferes con alertas de documentos
│   │   ├── App.jsx               # Router SPA + restauración de sesión JWT
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI + SQLAlchemy (patrón MVC)
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py           # RF01 — JWT + bcrypt
│   │   │   ├── rutas.py          # RF02 — CRUD rutas
│   │   │   ├── horarios.py       # RF03 — Programación + asignaciones
│   │   │   ├── choferes.py       # RF04 — Gestión de choferes
│   │   │   ├── dashboard.py      # RF06 — KPIs
│   │   │   └── conflictos.py     # RF03 — Listado y resolución de conflictos
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── ruta_service.py
│   │   │   ├── horario_service.py
│   │   │   ├── chofer_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── conflicto_service.py
│   │   ├── models/               # 11 modelos SQLAlchemy
│   │   │   ├── concesionario.py
│   │   │   ├── usuario.py
│   │   │   ├── estacion.py
│   │   │   ├── ruta.py
│   │   │   ├── chofer.py
│   │   │   ├── bus.py
│   │   │   ├── disponibilidad_chofer.py
│   │   │   ├── programacion.py
│   │   │   ├── horario_servicio.py
│   │   │   ├── asignacion.py
│   │   │   └── conflicto.py
│   │   ├── schemas/              # Validación Pydantic entrada/salida
│   │   ├── ia/
│   │   │   ├── prediccion.py     # RF05 — Prophet (pendiente)
│   │   │   └── optimizador.py    # RF05 — OR-Tools (pendiente)
│   │   ├── database.py           # Conexión PostgreSQL + SessionLocal
│   │   └── main.py               # Instancia FastAPI + CORS + routers
│   ├── db/
│   │   ├── schema.sql            # 11 tablas, triggers, vista v_dashboard_kpis
│   │   └── seed.sql              # Datos reales del Metropolitano
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml             # 4 servicios: backend, frontend, db, redis
├── .gitignore
└── README.md
```

---

## Instalación y ejecución

### Prerrequisitos

- Docker Desktop (recomendado)
- O bien: Node.js 20+, Python 3.11+, PostgreSQL 16, Redis 7

### Opción A — Con Docker Compose (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/MetroSmart/Metrohub.git
cd Metrohub

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar todos los servicios
docker-compose up --build
```

Los servicios quedan disponibles en:

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

La base de datos se inicializa automáticamente con `schema.sql` y `seed.sql` al primer arranque.

### Opción B — Solo frontend en desarrollo local

```bash
cd frontend
npm install
npm run dev
```

### Credenciales de demo

| Correo | Rol |
|--------|-----|
| admin.atu@metrosmart.gob.pe | Administrador ATU |
| sup.limavias@metrosmart.gob.pe | Supervisor Lima Vías Express |
| sup.limabus@metrosmart.gob.pe | Supervisor Lima Bus |
| sup.transvial@metrosmart.gob.pe | Supervisor Transvial |
| sup.perumasivo@metrosmart.gob.pe | Supervisor Perú Masivo |

> Las contraseñas están configuradas en el `.env` o son sus iniciales junto con un 123(Ej. limavias123 o admin123). La cuenta se bloquea tras 5 intentos fallidos (RF01).

---

## Uso del sistema

### 1. Login (RF01)
Accede con tu correo institucional desde la red interna ATU o VPN. El token JWT se almacena localmente y restaura la sesión automáticamente al recargar la página.

### 2. Dashboard (RF06)
Panel de control con KPIs operativos: rutas activas, choferes disponibles, buses operativos, conflictos pendientes y certificaciones Protransporte por vencer en los próximos 30 días. Los datos provienen directamente de PostgreSQL.

### 3. Rutas (RF02)
Catálogo de las 10 rutas del Metropolitano (A, B, C, Expresos 1-9, Nocturna) con tipo, horario de operación, frecuencia y estado activo/inactivo.

### 4. Programación / Grilla (RF03)
Selecciona una ruta y una fecha para visualizar los horarios de servicio con los choferes asignados y los conflictos activos. El Administrador ATU puede resolver conflictos directamente desde la interfaz.

### 5. Choferes (RF04)
Gestión del registro de choferes filtrable por estado. Los documentos próximos a vencer se resaltan con indicadores visuales de días restantes.

### 6. Optimizador IA *(RF05 — pendiente)*
Propuestas automáticas de programación usando Prophet y OR-Tools.

### 7. Exportación de reportes *(RF06 — pendiente)*
Generación de reportes en PDF y XLSX desde el dashboard.

---

## Gestión del proyecto — Scrum

El proyecto se gestiona con metodología Scrum con sprints semanales.

- GitHub: https://github.com/MetroSmart/Metrohub
- Rama activa: `main`
- Gestión de backlog: Jira (proyecto SCRUM)

### Product Backlog

| Ticket | Historia | Épica | Responsable | Estado |
|--------|----------|-------|-------------|--------|
| SCRUM-30 | Frontend — primera versión SPA | — | Erick | Resuelto |
| SCRUM-29 | Login con JWT y sesión persistente | RF01 | Cesar | Completado |
| SCRUM-28 | Autorización por roles | RF01 | Isaac | Completado |
| SCRUM-27 | Bloqueo por intentos fallidos y bcrypt | RF01 | Isaac/Cesar | Completado |
| SCRUM-23 | CRUD de rutas con atributos completos | RF02 | Isaac | Completado |
| SCRUM-22 | Activar/desactivar rutas | RF02 | Isaac/Cesar | Completado |
| SCRUM-24 | Gestión de estaciones | RF02 | Isaac | Parcial |
| SCRUM-19 | Grilla conectada al backend | RF03 | Cesar | Completado |
| SCRUM-18 | Validación y resolución de conflictos | RF03 | Isaac/Cesar | Completado |
| SCRUM-17 | Publicación aprobada para Supervisores | RF03 | Isaac | Pendiente |
| SCRUM-14 | Registro de choferes | RF04 | Cesar | Completado |
| SCRUM-16 | Asignación con reglas 8h y solapamiento | RF04 | Isaac | Completado |
| SCRUM-15 | Alertas de documentos por vencer | RF04 | Cesar | Completado |
| SCRUM-20 | Predicción de demanda (Prophet) | RF05 | Isaac/Cesar | Pendiente |
| SCRUM-21 | Optimizador OR-Tools | RF05 | Isaac | Pendiente |
| SCRUM-25 | Dashboard de KPIs desde BD | RF06 | Cesar | Completado |
| SCRUM-26 | Exportación PDF/XLSX | RF06 | Erick | Pendiente |

---

## Estado actual del sprint

### Sprint 1 — Arquitectura base e integración completa

Período: 23 – 30 abril 2026  
Objetivo: Sistema funcionando de punta a punta — backend MVC + frontend React + PostgreSQL integrados

| Integrante | Actividades principales |
|------------|------------------------|
| **Isaac Martel** | Backend principal (modelos, routers, servicios), schema BD, Docker Compose, integración final del sistema |
| **Cesar Correa** | Backend , `api.js`, fusión frontend-backend, conexión de todas las páginas a la API |
| **Erick Ortega** | Frontend completo (páginas y componentes), diseño visual, gestión del backlog en Jira |
| **Diego Torres** | `seed.sql` con datos simulados del Metropolitano (52 horarios, 20 choferes, 16 buses, 3 conflictos) |
| **Ivett Mera** | Soporte en Jira, investigación de datos reales del Metropolitano |

**Avance:** 13 de 17 ítems completados — **76 %**

---

## Estándares de código

### Frontend
- Linter: ESLint
- Naming: camelCase (variables), PascalCase (componentes)
- Estructura: funcionales con Hooks
- HTTP: módulo centralizado `api.js` — sin llamadas directas en componentes

### Backend
- Linter: PEP 8
- Framework: FastAPI con patrón MVC
- ORM: SQLAlchemy 2.0
- Documentación: docstrings en español

---

## Contribución

### Rama de trabajo
```bash
git checkout -b SCRUM-XX-descripcion-corta
git add .
git commit -m "SCRUM-XX: descripción clara del cambio"
git push origin SCRUM-XX-descripcion-corta
```

### Pull Request
- Describe qué cambios realizas
- Referencia el ticket Scrum
- Solicita review de un compañero

---

## Referencias

- IEEE Std 830-1998 — Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2011 — Systems and Software Engineering: Requirements Engineering
- Datos públicos del Metropolitano de Lima — ATU (https://www.atu.gob.pe)
- Ley No. 29733 — Ley de Protección de Datos Personales del Perú
- FastAPI Documentation (https://fastapi.tiangolo.com)
- SQLAlchemy Documentation (https://docs.sqlalchemy.org)
- OR-Tools — Google (https://developers.google.com/optimization)
- Prophet — Meta (https://facebook.github.io/prophet/)

---

MetroHub v1.0 · Universidad Nacional de Ingeniería · Lima, Perú · 2026
