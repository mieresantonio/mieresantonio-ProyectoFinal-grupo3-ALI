"""Configuración compartida de la suite del backend de Blockali.

La app se importa UNA vez con una BD SQLite temporal y el correo
sustituido por un buzón falso que captura los mensajes (así los tests
pueden extraer los tokens reales de verificación/recuperación de los
enlaces, igual que haría un usuario desde su bandeja de entrada).
"""
import os
import re
import sys
import tempfile
import uuid

# El entorno debe fijarse ANTES de importar la app (app.py lee env al cargar).
_TMP = tempfile.mkdtemp(prefix="blockali-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["FLASK_APP_KEY"] = "test-secret-key"
os.environ.pop("FLASK_DEBUG", None)
os.environ.pop("ENABLE_ADMIN", None)
# La suite ES un entorno controlado y varios fixtures inician sesión con
# ambas cuentas demo: el estudiante demo se siembra siempre, pero el
# admin demo solo se crea con SEED_DEMO_USERS=1, así que aquí se activa
# explícitamente.
os.environ["SEED_DEMO_USERS"] = "1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from api.models import db  # noqa: E402
import api.routes as routes  # noqa: E402


class FakeMail:
    """Sustituto de flask-mail: captura los mensajes en vez de enviarlos."""

    def __init__(self):
        self.sent = []

    def send(self, msg):
        self.sent.append(msg)


@pytest.fixture(scope="session")
def app():
    return flask_app


@pytest.fixture(scope="session")
def fake_mail():
    fake = FakeMail()
    routes.mail = fake
    return fake


@pytest.fixture(scope="session")
def seeded(app, fake_mail):
    """BD creada y semilla corrida (la misma que usa producción)."""
    with app.app_context():
        db.create_all()
        result = app.test_cli_runner().invoke(args=["insert-test-data"])
        assert result.exit_code == 0, result.output
    return app


@pytest.fixture()
def client(seeded):
    return seeded.test_client()


def _token_del_correo(fake_mail, fragmento):
    """Extrae el ?token= del último correo cuyo asunto contiene fragmento."""
    for msg in reversed(fake_mail.sent):
        if fragmento in (msg.subject or ""):
            m = re.search(r"token=([\w.\-]+)", msg.html or "")
            assert m, f"sin token en el correo: {msg.subject}"
            return m.group(1)
    raise AssertionError(f"no llegó correo con asunto ~ {fragmento!r}")


@pytest.fixture()
def nuevo_usuario(client, fake_mail):
    """Registra, verifica y loguea un usuario nuevo; devuelve (headers, user)."""
    def crear():
        sufijo = uuid.uuid4().hex[:10]
        email = f"test.{sufijo}@example.test"
        r = client.post("/api/signup", json={
            "username": f"User {sufijo}",
            "email": email,
            "password": "secret123",
        })
        assert r.status_code == 201, r.get_json()
        token = _token_del_correo(fake_mail, "Verifica tu cuenta")
        r = client.post("/api/verify-email", json={"token": token})
        assert r.status_code == 200, r.get_json()
        r = client.post("/api/login", json={
            "email": email, "password": "secret123"})
        assert r.status_code == 200, r.get_json()
        data = r.get_json()
        return {"Authorization": f"Bearer {data['token']}"}, data["user"]

    return crear


@pytest.fixture()
def admin_headers(client):
    r = client.post("/api/login", json={
        "email": "admin@academy.test", "password": "Admin123!"})
    assert r.status_code == 200, r.get_json()
    return {"Authorization": f"Bearer {r.get_json()['token']}"}


@pytest.fixture()
def student_headers(client):
    r = client.post("/api/login", json={
        "email": "student@academy.test", "password": "Student123!"})
    assert r.status_code == 200, r.get_json()
    return {"Authorization": f"Bearer {r.get_json()['token']}"}
