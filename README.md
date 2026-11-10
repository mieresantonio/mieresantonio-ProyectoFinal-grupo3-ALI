# Blockali — Plataforma de aprendizaje de Blockchain

**Aprende blockchain haciendo.** Blockali es una plataforma educativa en español con rutas de aprendizaje guiadas: lecciones en profundidad, quizzes con nota real, progreso persistente en tu cuenta y un enfoque honesto — *hecho para aprender, no para especular*.

Nació como proyecto final del bootcamp Full Stack de **4Geeks Academy (Grupo 3)** y sigue evolucionando como producto.

## App en vivo

**[BC123.pythonanywhere.com](https://BC123.pythonanywhere.com)** — Contenido actual: 2 rutas, 5 módulos, 9 lecciones con sus 9 quizzes, y el tutor integrado en [`/tutor`](https://BC123.pythonanywhere.com/tutor).

## Qué ofrece

- **Cuentas completas** — registro con verificación de correo, inicio de sesión con JWT, recuperación de contraseña y roles (estudiante / administrador).
- **Rutas de aprendizaje** — rutas → módulos → lecciones en Markdown, con desbloqueo secuencial.
- **Quizzes con nota real** — cada lección se evalúa; se aprueba con 70% o más y la nota queda registrada.
- **Progreso persistente** — panel del estudiante con % de avance, quizzes aprobados y siguiente lección.
- **Contenido inicial**:
  - *Fundamentos de Blockchain* — conceptos esenciales, criptografía y wallets, transacciones paso a paso y consenso (Proof of Work y Proof of Stake). Lecciones completas en Markdown, con ejemplos e idea clave final.
  - *Desarrollo de Smart Contracts* — estructura de Solidity, funciones y visibilidad, eventos y errores, y seguridad esencial (patrón checks-effects-interactions).
- **Tutor integrado** — en `/tutor`: responde preguntas usando solo el contenido de las lecciones, con cita de la lección de origen (ver más abajo).
- **Ticker de precios** cripto en vivo en la portada.
- **Panel de administración** para gestionar usuarios y contenido.

## Lo nuevo: diseño web3, laboratorio, gamificación y certificados

### Diseño oscuro web3 (fase 1)
Sistema de diseño propio en tema oscuro con tokens de color, degradados y
Lucide como único set de iconos. La portada se rediseñó como landing de
producto y todas las páginas se adaptaron al mismo sistema.

### Laboratorio interactivo — `/laboratorio`
Aprende tocando, no solo leyendo:
- **SHA-256 en vivo**: escribe un texto y ve su hash al instante.
- **Cadena de 3 bloques manipulable**: cambia el contenido de un bloque y
  observa cómo se rompe la cadena a partir de ese punto.

### Gamificación
El progreso da recompensas visibles:
- **XP**: 100 puntos por cada lección completada, más los puntos de los
  quizzes.
- **6 niveles**: Explorador → Aprendiz de bloques → Constructor →
  Validador → Nodo completo → Arquitecto Web3.
- **Rachas**: días consecutivos de actividad, calculados desde el
  progreso registrado.

### Certificados verificables
Al completar una ruta al 100% (todas las lecciones) con todos los quizzes
aprobados (≥70%), puedes reclamar un certificado con código único
`BK-XXXXX-XXXXX-XXXXX`:
- **Certificado imprimible** en `/certificado/:pathId`.
- **Verificación pública** en `/verificar/:code`: cualquiera puede
  comprobar que un código corresponde a un certificado real.

### Tutor de lecciones — `/tutor`
Un tutor dentro de la plataforma que responde preguntas del estudiante
usando **únicamente el contenido de las lecciones de Blockali**:

- **Endpoint** `POST /api/tutor`: búsqueda TF-IDF (solo librería
  estándar de Python) sobre los fragmentos de las lecciones; sin
  servicios externos, sin claves de API y sin modelos de lenguaje.
- **Respuesta extractiva con fuentes**: compone la respuesta con los
  fragmentos más relevantes y cita ruta, módulo y lección, con enlace
  directo a cada lección.
- **Honesto por diseño**: si el tema no está en las lecciones, lo dice
  y sugiere la lección más cercana en vez de inventar una respuesta.

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | React 18 + Vite, React Router 6, Bootstrap 5 (sistema de diseño propio en tema oscuro) |
| Backend | Flask, SQLAlchemy 2, Flask-JWT-Extended, Flask-Mail, Alembic |
| Base de datos | SQLite (producción y desarrollo, vía SQLAlchemy) |
| Despliegue | PythonAnywhere (producción) · `render.yaml` incluido como plantilla alternativa, sin despliegue activo |

## Ejecutar en local

Requisitos: Python 3.13 con Pipenv y Node ≥ 20.

```bash
# 1) Dependencias
pipenv install
npm install

# 2) Variables de entorno
cp .env.example .env   # ajusta DATABASE_URL, FLASK_APP_KEY y credenciales de correo

# 3) Base de datos y contenido inicial
pipenv run flask db upgrade
pipenv run flask insert-test-data

# 4) Servidores (dos terminales)
pipenv run start       # API Flask en :3001
npm run dev            # Frontend Vite en :3000 (proxy /api → :3001)
```

> **Cuentas demo:** `insert-test-data` siempre crea el contenido (rutas, módulos, lecciones y quizzes) y la cuenta de **estudiante demo** (`student@academy.test` / `Student123!`, rol estudiante y sin privilegios): es el ingreso público de prueba, para entrar a ver la plataforma sin registrarse. La cuenta de **administrador demo** (`admin@academy.test`, de contraseña conocida) solo se crea si el entorno trae `SEED_DEMO_USERS=1`: úsala únicamente en entornos controlados (local/pruebas) y no pongas nunca esa variable en un despliegue público.

## Estructura

```
src/
  api/          API Flask: modelos, rutas, comandos, correo
  app.py        Entrada del backend
  front/
    pages/      Vistas (Home, Courses, Dashboard, Lesson, Quiz, Admin…)
    components/ Navbar, Hero, tarjetas de curso, Login/Register…
    services/   Clientes de la API (cursos, quizzes, precios)
    hooks/      Store global (useGlobalReducer)
migrations/     Migraciones de base de datos (Alembic)
docs/           Documentación auxiliar
```

## Seguridad

- Contraseñas con hash (Werkzeug), nunca en texto plano.
- Endpoints de progreso y administración protegidos con JWT y verificación de dueño/rol.
- Verificación de correo antes de activar la cuenta.

## Mi aporte

Blockali nació como el proyecto final grupal del Grupo 3 sobre la plantilla react-flask de 4Geeks Academy. Además de mi parte en la construcción de la base junto al grupo, lideré su evolución posterior hasta convertirla en un producto en producción:

- **Contenido y tutor integrado**: lecciones completas en Markdown con sus quizzes, y el tutor que responde solo desde el contenido de las lecciones, citando la fuente.
- **Revisión de seguridad del backend**: administración protegida, permisos por dueño y rol, y cuentas demo con acceso controlado en producción.
- **Gamificación y certificados verificables**: XP, niveles, rachas y certificados con código único y verificación pública.
- **Despliegue y mantenimiento**: puesta en producción en PythonAnywhere y evolución continua.

Soy el autor con más commits del repositorio (44 de 89).

La evolución posterior de Blockali se desarrolló con apoyo de herramientas de IA como par de programación, bajo mi dirección y revisión: cada cambio de arquitectura, seguridad y despliegue fue verificado antes de publicarse.

## Créditos

Proyecto final de 4Geeks Academy — Grupo 3 (ALI). Construido sobre la plantilla oficial react-flask de 4Geeks, muy modificada.
