# Blockali — Plataforma de aprendizaje de Blockchain

**Aprende blockchain haciendo.** Blockali es una plataforma educativa en español con rutas de aprendizaje guiadas: lecciones en profundidad, quizzes con nota real, progreso persistente en tu cuenta y un enfoque honesto — *hecho para aprender, no para especular*.

Nació como proyecto final del bootcamp Full Stack de **4Geeks Academy (Grupo 3)** y sigue evolucionando como producto.

## Qué ofrece

- **Cuentas completas** — registro con verificación de correo, inicio de sesión con JWT, recuperación de contraseña y roles (estudiante / administrador).
- **Rutas de aprendizaje** — rutas → módulos → lecciones en Markdown, con desbloqueo secuencial.
- **Quizzes con nota real** — cada lección se evalúa; se aprueba con 70% o más y la nota queda registrada.
- **Progreso persistente** — panel del estudiante con % de avance, quizzes aprobados y siguiente lección.
- **Contenido inicial**:
  - *Fundamentos de Blockchain* — conceptos esenciales, criptografía y wallets, consenso (Proof of Work).
  - *Desarrollo de Smart Contracts* — estructura de Solidity y primer contrato.
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

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | React 18 + Vite, React Router 6, Bootstrap 5 (sistema de diseño propio en tema oscuro) |
| Backend | Flask, SQLAlchemy 2, Flask-JWT-Extended, Flask-Mail, Alembic |
| Base de datos | PostgreSQL (SQLite en desarrollo) |
| Despliegue | Render (`render.yaml` + `render_build.sh`) |

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

## Créditos

Proyecto final de 4Geeks Academy — Grupo 3 (ALI). Construido sobre la plantilla oficial react-flask de 4Geeks, muy modificada.
