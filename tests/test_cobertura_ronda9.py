"""Caracterización de la Ronda 9 (Bucle 1): zonas sin cobertura de la suite.

La medición previa (coverage 7.10.7, ver LOG-RONDA-9-B1.md) dejó
45 líneas sin cubrir en routes.py (92 %), utils.py al 27 % y el camino
ACTIVO de setup_admin sin ejecutar. Cada test de este fichero fija el
comportamiento ACTUAL de una de esas zonas, elegido por ser verificable
sin ambigüedad desde el código y la semilla existente:

- ramas de validación/error de auth que devuelven JSON determinista;
- el endpoint /hello, nunca llamado por la suite;
- el éxito de /modules/<id> y de /dashboard (solo se probaban errores);
- el 403 del progreso de una lección ajena y el quiz_score inválido
  en el POST de progreso (solo se probaba en el PUT);
- las ramas de fallo de correo (signup -> 500 JSON; forgot -> 200
  genérico igualmente), inyectando el fallo en el FakeMail de conftest;
- helpers puros (_calcular_rachas, _tutor_fragmentos, _tutor_coseno)
  y el nivel máximo de gamificación por la API completa;
- utils.py entero (APIException, has_no_empty_params, generate_sitemap)
  y setup_admin activado sobre una app Flask desechable.

Las ÚNICAS líneas de routes.py que quedan sin cubrir tras esta ronda
son los dos `except` genéricos de POST/PUT /progress (500 al fallar el
commit): forzarlos exige inyectar un fallo de BD sobre la sesión
compartida de la suite, y su comportamiento es el patrón genérico
rollback + 500 con str(error). Quedan documentadas en el log.
"""
import uuid
from datetime import datetime, time, timedelta, timezone
from types import SimpleNamespace

from flask import Flask
from flask_jwt_extended import create_access_token

import api.routes as routes
from api.admin import setup_admin
from api.routes import _calcular_rachas, _tutor_coseno, _tutor_fragmentos
from api.utils import APIException, generate_sitemap, has_no_empty_params


def _email_unico():
    return f"r9.{uuid.uuid4().hex[:10]}@example.test"


def _signup(client, email, username="R9", password="secret123"):
    r = client.post("/api/signup", json={
        "username": username, "email": email, "password": password})
    assert r.status_code == 201, r.get_json()
    return r


# ---------------------------------------------------------------------------
# /hello — el endpoint nunca era llamado por la suite (líneas 332, 336)
# ---------------------------------------------------------------------------

_HELLO_MSG = (
    "Hello! I'm a message that came from the backend, check the network "
    "tab on the google inspector and you will see the GET request")


def test_hello_get_y_post_devuelven_el_mensaje_del_backend(client):
    for metodo in (client.get, client.post):
        r = metodo("/api/hello")
        assert r.status_code == 200
        assert r.get_json() == {"message": _HELLO_MSG}


# ---------------------------------------------------------------------------
# Signup: contraseña no-cadena (94), longitud excesiva (97),
# re-registro de cuenta inactiva (111-113) y fallo de correo (157-160)
# ---------------------------------------------------------------------------

def test_signup_password_no_cadena_da_400_no_500(client):
    r = client.post("/api/signup", json={
        "username": "R9", "email": _email_unico(), "password": 123456})
    assert r.status_code == 400
    assert r.is_json
    assert "al menos 6 caracteres" in r.get_json()["error"]


def test_signup_username_o_email_demasiado_largos_da_400(client):
    r = client.post("/api/signup", json={
        "username": "x" * 81, "email": _email_unico(),
        "password": "secret123"})
    assert r.status_code == 400
    assert r.get_json()["error"] == (
        "El correo o el nombre de usuario son demasiado largos")
    r = client.post("/api/signup", json={
        "username": "R9", "email": "a" * 109 + "@example.test",
        "password": "secret123"})
    assert r.status_code == 400
    assert "demasiado largos" in r.get_json()["error"]


def test_signup_re_registro_de_cuenta_inactiva_actualiza_y_verifica(
        client, fake_mail):
    from conftest import _token_del_correo

    email = _email_unico()
    _signup(client, email, username="Primero", password="primera123")
    # La cuenta sigue inactiva (sin verificar): registrarse de nuevo con
    # el mismo correo NO da «ya registrado», actualiza nombre y clave.
    r = client.post("/api/signup", json={
        "username": "Segundo", "email": email, "password": "segunda123"})
    assert r.status_code == 201, r.get_json()

    token = _token_del_correo(fake_mail, "Verifica tu cuenta")
    r = client.post("/api/verify-email", json={"token": token})
    assert r.status_code == 200, r.get_json()
    # Entra con la clave NUEVA y el nombre NUEVO; la primera clave muere.
    r = client.post("/api/login", json={
        "email": email, "password": "segunda123"})
    assert r.status_code == 200
    assert r.get_json()["user"]["username"] == "Segundo"
    r = client.post("/api/login", json={
        "email": email, "password": "primera123"})
    assert r.status_code == 401


def test_signup_fallo_de_correo_da_500_json_y_la_cuenta_queda_creada(
        client, fake_mail, monkeypatch):
    def boom(msg):
        raise RuntimeError("SMTP caído (sonda R9)")

    monkeypatch.setattr(fake_mail, "send", boom)
    email = _email_unico()
    r = client.post("/api/signup", json={
        "username": "R9", "email": email, "password": "secret123"})
    assert r.status_code == 500
    assert r.is_json
    body = r.get_json()
    assert body["message"] == (
        "Usuario registrado, pero hubo un error al enviar el correo.")
    assert "SMTP caído" in body["error"]
    # El commit del usuario es ANTERIOR al envío: la cuenta existe pero
    # inactiva, así que el login responde 403 (sin verificar), no 401.
    monkeypatch.undo()
    r = client.post("/api/login", json={
        "email": email, "password": "secret123"})
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Login: contraseña no-cadena (177)
# ---------------------------------------------------------------------------

def test_login_password_no_cadena_da_401_no_500(client):
    r = client.post("/api/login", json={
        "email": "student@academy.test", "password": 123456})
    assert r.status_code == 401
    assert r.get_json()["error"] == "Credenciales inválidas"


# ---------------------------------------------------------------------------
# Verify-email: tipo de token (203), usuario inexistente (211),
# cuenta ya verificada (213)
# ---------------------------------------------------------------------------

def _token_fantasma(app, tipo):
    with app.app_context():
        return create_access_token(
            identity="fantasma.r9@example.test",
            additional_claims={"type": tipo})


def test_verify_con_token_de_recuperacion_da_400_tipo_invalido(client, app):
    token = _token_fantasma(app, "reset_password")
    r = client.post("/api/verify-email", json={"token": token})
    assert r.status_code == 400
    assert r.get_json()["error"] == "Tipo de token inválido"


def test_verify_usuario_inexistente_da_404(client, app):
    token = _token_fantasma(app, "verify_email")
    r = client.post("/api/verify-email", json={"token": token})
    assert r.status_code == 404
    assert r.get_json()["error"] == "Usuario no encontrado"


def test_verify_por_segunda_vez_da_ya_verificada(client, fake_mail):
    from conftest import _token_del_correo

    _signup(client, _email_unico())
    token = _token_del_correo(fake_mail, "Verifica tu cuenta")
    r = client.post("/api/verify-email", json={"token": token})
    assert r.status_code == 200
    assert "verificada exitosamente" in r.get_json()["message"]
    # El mismo token, ya con la cuenta activa: 200 informativo, no error.
    r = client.post("/api/verify-email", json={"token": token})
    assert r.status_code == 200
    assert r.get_json()["message"] == (
        "Tu cuenta ya se encuentra verificada.")


# ---------------------------------------------------------------------------
# Forgot-password: el fallo de correo se traga y se responde 200 (278-279)
# ---------------------------------------------------------------------------

def test_forgot_fallo_de_correo_responde_200_generico_igualmente(
        client, nuevo_usuario, fake_mail, monkeypatch):
    _, user = nuevo_usuario()

    def boom(msg):
        raise RuntimeError("SMTP caído (sonda R9)")

    monkeypatch.setattr(fake_mail, "send", boom)
    r = client.post("/api/forgot-password", json={"email": user["email"]})
    assert r.status_code == 200
    assert r.get_json()["message"] == (
        "Si el correo existe, hemos enviado las instrucciones para "
        "restablecer tu contraseña.")


# ---------------------------------------------------------------------------
# Reset-password: clave corta (301), tipo de token (306),
# usuario inexistente (314) y token inválido (321-322)
# ---------------------------------------------------------------------------

def test_reset_password_demasiado_corta_da_400(client):
    # La longitud se valida ANTES de decodificar el token.
    r = client.post("/api/reset-password", json={
        "token": "lo-que-sea", "password": "123"})
    assert r.status_code == 400
    assert "al menos 6 caracteres" in r.get_json()["error"]


def test_reset_con_token_de_verificacion_da_400_tipo_invalido(client, app):
    token = _token_fantasma(app, "verify_email")
    r = client.post("/api/reset-password", json={
        "token": token, "password": "nuevaClave9"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "Tipo de token inválido"


def test_reset_usuario_inexistente_da_404(client, app):
    token = _token_fantasma(app, "reset_password")
    r = client.post("/api/reset-password", json={
        "token": token, "password": "nuevaClave9"})
    assert r.status_code == 404
    assert r.get_json()["error"] == "Usuario no encontrado"


def test_reset_token_invalido_da_400_con_detalle(client):
    r = client.post("/api/reset-password", json={
        "token": "token-malo", "password": "nuevaClave9"})
    assert r.status_code == 400
    body = r.get_json()
    assert body["error"] == "El enlace es inválido o ha expirado."
    assert body["detail"]


# ---------------------------------------------------------------------------
# Catálogo y dashboard: los éxitos que solo se probaban por el error
# ---------------------------------------------------------------------------

def test_detalle_de_modulo_ok(client):
    modules = client.get("/api/modules").get_json()
    primero = modules[0]
    r = client.get(f"/api/modules/{primero['id']}")
    assert r.status_code == 200
    # Forma exacta del detalle: solo id, title y level (sin lessons).
    assert r.get_json() == {
        "id": primero["id"], "title": primero["title"],
        "level": primero["level"]}


def test_dashboard_ok_devuelve_bienvenida_y_usuario(client, student_headers):
    r = client.get("/api/dashboard", headers=student_headers)
    assert r.status_code == 200
    body = r.get_json()
    assert body["message"] == "Bienvenido"
    assert body["user"]["email"] == "student@academy.test"
    assert body["user"]["role"] == "student"


# ---------------------------------------------------------------------------
# Progreso: 403 en la lección individual ajena (575) y quiz_score
# inválido en el POST (606; hasta ahora solo se fijaba en el PUT)
# ---------------------------------------------------------------------------

def test_progreso_de_leccion_ajena_da_403(client, nuevo_usuario):
    headers, _ = nuevo_usuario()
    _, otro = nuevo_usuario()
    lid = client.get("/api/lessons").get_json()[0]["id"]
    r = client.get(f"/api/progress/{otro['id']}/{lid}", headers=headers)
    assert r.status_code == 403
    assert "error" in r.get_json()


def test_post_progreso_quiz_score_invalido_da_400_y_no_crea_nada(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = client.get("/api/lessons").get_json()[0]["id"]
    for malo in (150, -1, "cien", True):
        r = client.post("/api/progress", headers=headers, json=[
            {"user_id": user["id"], "lesson_id": lid, "quiz_score": malo}])
        assert r.status_code == 400, malo
        assert r.get_json()["error"] == (
            "quiz_score debe ser un número entre 0 y 100")
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert r.get_json() == []


# ---------------------------------------------------------------------------
# Certificados con un token de CORREO como Bearer: la identidad es el
# email, no un id -> claim 404 «Usuario no encontrado» (837) y
# /certificates/mine 403 (885). Complementa la regresión B3, que solo
# cubría /dashboard, /gamification/me y /users.
# ---------------------------------------------------------------------------

def _headers_token_de_correo(client, fake_mail):
    _signup(client, _email_unico())
    from conftest import _token_del_correo
    token = _token_del_correo(fake_mail, "Verifica tu cuenta")
    return {"Authorization": f"Bearer {token}"}


def test_claim_con_token_de_correo_da_404_usuario_no_encontrado(
        client, fake_mail):
    headers = _headers_token_de_correo(client, fake_mail)
    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": 1})
    assert r.status_code == 404
    assert r.get_json()["error"] == "Usuario no encontrado"


def test_certificates_mine_con_token_de_correo_da_403(client, fake_mail):
    headers = _headers_token_de_correo(client, fake_mail)
    r = client.get("/api/certificates/mine", headers=headers)
    assert r.status_code == 403
    assert "error" in r.get_json()


# ---------------------------------------------------------------------------
# Gamificación: usuario sin actividad (756 por HTTP), _calcular_rachas
# como unidad (756, 760-761, 768-769) y nivel máximo (791-792)
# ---------------------------------------------------------------------------

def test_gamificacion_usuario_nuevo_todo_a_cero(client, nuevo_usuario):
    headers, _ = nuevo_usuario()
    r = client.get("/api/gamification/me", headers=headers)
    assert r.status_code == 200
    body = r.get_json()
    assert body["xp"] == 0
    assert body["level_name"] == "Explorador"
    assert body["level_min_xp"] == 0
    assert body["next_level_name"] == "Aprendiz de bloques"
    assert body["next_level_xp"] == 300
    assert body["xp_to_next"] == 300
    assert body["progress_to_next"] == 0.0
    assert body["streak_current"] == 0
    assert body["streak_best"] == 0
    assert body["active_days"] == 0
    assert body["lessons_completed"] == 0
    assert body["quizzes_passed"] == 0


def _al_mediodia(d):
    return datetime.combine(d, time(12, 0), tzinfo=timezone.utc)


def test_calcular_rachas_sin_fechas_o_solo_nulas():
    assert _calcular_rachas([]) == (0, 0, 0)
    assert _calcular_rachas([None, None]) == (0, 0, 0)


def test_calcular_rachas_consecutiva_hasta_hoy():
    hoy = datetime.now(timezone.utc).date()
    fechas = [_al_mediodia(hoy - timedelta(days=d)) for d in (2, 0, 1)]
    # Desordenadas a propósito: la función ordena y deduplica por día.
    assert _calcular_rachas(fechas) == (3, 3, 3)
    assert _calcular_rachas([_al_mediodia(hoy), _al_mediodia(hoy)]) == (1, 1, 1)
    assert _calcular_rachas(
        [_al_mediodia(hoy - timedelta(days=1))]) == (1, 1, 1)


def test_calcular_rachas_con_hueco_y_racha_antigua():
    hoy = datetime.now(timezone.utc).date()
    # Hueco de un día: la racha actual es solo hoy; la mejor también 1.
    fechas = [_al_mediodia(hoy), _al_mediodia(hoy - timedelta(days=2))]
    assert _calcular_rachas(fechas) == (1, 1, 2)
    # Racha antigua de 2 que NO llega a hoy ni a ayer: actual 0.
    fechas = [_al_mediodia(hoy - timedelta(days=10)),
              _al_mediodia(hoy - timedelta(days=9))]
    assert _calcular_rachas(fechas) == (0, 2, 2)


def test_gamificacion_nivel_maximo_sin_siguiente(
        client, nuevo_usuario, admin_headers):
    r = client.post("/api/learning-paths", headers=admin_headers, json={
        "title": "Ruta Nivel Máximo R9", "level": "Avanzado"})
    assert r.status_code == 201
    path_id = r.get_json()["id"]
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo Nivel Máximo R9", "level": "Avanzado",
        "learning_path_id": path_id})
    assert r.status_code == 201
    module_id = r.get_json()["id"]
    # 17 lecciones x (100 de completar + 100 de quiz) = 3400 XP >= 3200.
    lesson_ids = []
    for i in range(1, 18):
        r = client.post("/api/lessons", headers=admin_headers, json={
            "title": f"Lección Nivel Máximo {i}",
            "content": f"Material de práctica guiada número {i} del nivel máximo.",
            "module_id": module_id, "order_number": i})
        assert r.status_code == 201
        lesson_ids.append(r.get_json()["id"])

    headers, user = nuevo_usuario()
    for lid in lesson_ids:
        r = client.put(f"/api/progress/{user['id']}/{lid}",
                       headers=headers,
                       json={"is_completed": True, "quiz_score": 100})
        assert r.status_code == 200

    r = client.get("/api/gamification/me", headers=headers)
    assert r.status_code == 200
    body = r.get_json()
    assert body["xp"] == 3400
    assert body["level_name"] == "Arquitecto Web3"
    assert body["level_min_xp"] == 3200
    assert body["next_level_name"] is None
    assert body["next_level_xp"] is None
    assert body["xp_to_next"] == 0
    assert body["progress_to_next"] == 1.0
    assert body["lessons_completed"] == 17
    assert body["quizzes_passed"] == 17


# ---------------------------------------------------------------------------
# Tutor: ramas internas de los helpers (976, 986, 1083) y el endpoint
# sin ninguna lección en el índice (1123)
# ---------------------------------------------------------------------------

_LARGO = ("La cadena de bloques registra cada transacción de forma "
          "pública y permanente para todos los participantes.")


def test_tutor_fragmentos_bloque_que_limpia_a_vacio_se_omite():
    # "###" es un bloque Markdown que al limpiarse queda '': se salta.
    assert _tutor_fragmentos("###\n\n" + _LARGO) == [_LARGO]


def test_tutor_fragmentos_cola_corta_se_fusiona_con_el_ultimo():
    assert _tutor_fragmentos(_LARGO + "\n\nFin.") == [_LARGO + " Fin."]
    # Y una pieza corta SOLA sí forma fragmento propio.
    assert _tutor_fragmentos("Hola") == ["Hola"]


def test_tutor_coseno_sin_tokens_o_sin_norma_da_cero():
    doc = {"norma": 1.0, "vector": {"blockchain": 1.0}}
    assert _tutor_coseno([], {}, doc) == 0.0
    assert _tutor_coseno(["blockchain"], {}, {"norma": 0.0, "vector": {}}) == 0.0


def test_tutor_sin_lecciones_en_el_indice_responde_honesto(
        client, monkeypatch):
    monkeypatch.setattr(routes, "_tutor_indice", lambda: ([], {}))
    r = client.post("/api/tutor", json={"question": "¿Qué es una blockchain?"})
    assert r.status_code == 200
    assert r.get_json() == {
        "found": False,
        "answer": "Todavía no hay lecciones cargadas en la plataforma.",
        "sources": [],
    }


# ---------------------------------------------------------------------------
# utils.py — APIException (7-16), has_no_empty_params (19-21) y
# generate_sitemap (24-34); solo se importaba, nunca se ejecutaba.
# ---------------------------------------------------------------------------

def test_api_exception_por_defecto_y_personalizada():
    e = APIException("boom")
    assert e.status_code == 400
    assert e.message == "boom"
    assert e.payload is None
    assert e.to_dict() == {"message": "boom"}

    e = APIException("boom", status_code=418, payload={"extra": 1})
    assert e.status_code == 418
    assert e.to_dict() == {"extra": 1, "message": "boom"}


def test_has_no_empty_params_casos():
    assert has_no_empty_params(
        SimpleNamespace(defaults=None, arguments=None)) is True
    assert has_no_empty_params(
        SimpleNamespace(defaults=(), arguments=())) is True
    assert has_no_empty_params(
        SimpleNamespace(defaults=("d",), arguments=("x",))) is True
    assert has_no_empty_params(
        SimpleNamespace(defaults=(), arguments=("x",))) is False
    assert has_no_empty_params(
        SimpleNamespace(defaults=None, arguments=("x",))) is False


def test_generate_sitemap_lista_las_rutas_get_sin_parametros(app):
    with app.test_request_context():
        html = generate_sitemap(app)
    assert "Rigo welcomes you to your API!!" in html
    # /api/hello es GET y sin parámetros: debe aparecer enlazada.
    assert "<li><a href='/api/hello'>/api/hello</a></li>" in html
    assert "<li><a href='/'>/</a></li>" in html


# ---------------------------------------------------------------------------
# admin.py — el camino ACTIVO de setup_admin (22-29), sobre una app
# desechable para no registrar Flask-Admin en la app de la suite.
# ---------------------------------------------------------------------------

def test_setup_admin_activado_registra_admin_y_una_vista_por_modelo(
        monkeypatch):
    monkeypatch.setenv("ENABLE_ADMIN", "1")
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    fresh = Flask("test_admin_r9")
    setup_admin(fresh)
    assert "admin" in fresh.blueprints
    # Una vista (blueprint) por cada modelo: user, learningpath, etc.
    for nombre in ("user", "learningpath", "module", "lesson",
                   "quiz", "userprogress", "certificate"):
        assert nombre in fresh.blueprints, nombre
