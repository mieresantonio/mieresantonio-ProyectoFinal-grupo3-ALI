"""Tests de regresión de las rondas 2 y 3 (operación de mejora, nov 2026).

Cada test fija una corrección YA aplicada y verificada por sonda en
esas rondas (ver LOG-RONDA-2-B1.md y LOG-RONDA-3-B1.md en la carpeta
de la operación): si alguien revierte la corrección, el test debe
fallar. No reescriben ningún test anterior; los complementan:

- B1: reset-password con contraseña no-cadena -> 400 (antes 500 HTML).
- B2: cuerpo JSON válido pero no-objeto -> 400 JSON (antes 500 HTML).
- B3: token de verificación/recuperación como Bearer -> 403 JSON
  (antes 500 por ValueError en int(get_jwt_identity())).
- B4: progreso con lesson_id inexistente -> 404 y el GET de la cuenta
  sigue sano (antes 201 huérfano y GET posterior en 500).
- B5: is_completed no booleano -> 400 (antes 500 con el SQL filtrado).
- B6: create_lesson con order_number no numérico -> 400 (antes 201).
- Ronda 3 §1: el tutor responde idéntico con la caché fría y caliente,
  y una edición de contenido invalida la caché.
- Ronda 3 §2: los endpoints con N+1 corregido (/modules, /progress,
  /certificates/mine) devuelven el mismo contenido que la semántica
  previa al eager loading (igualdad de cuerpo, no de SQL).
"""
import uuid

import api.routes as routes
from api.models import db, Lesson


# ---------------------------------------------------------------------------
# B1 — reset-password con contraseña no-cadena
# ---------------------------------------------------------------------------

def test_regresion_reset_password_no_cadena_da_400_no_500(
        client, nuevo_usuario, fake_mail):
    from conftest import _token_del_correo

    headers, user = nuevo_usuario()
    r = client.post("/api/forgot-password", json={"email": user["email"]})
    assert r.status_code == 200
    token = _token_del_correo(fake_mail, "Recuperación de contraseña")

    # Sonda 1 de la ronda 2: "password": 123456 -> TypeError en len()
    # y 500 HTML. Con token VÁLIDO, para aislar la validación de tipo.
    r = client.post("/api/reset-password", json={
        "token": token, "password": 123456})
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()

    # La contraseña anterior sigue intacta (no hubo cambio parcial).
    r = client.post("/api/login", json={
        "email": user["email"], "password": "secret123"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# B2 — cuerpos JSON válidos pero no-objeto
# ---------------------------------------------------------------------------

def test_regresion_signup_cuerpo_no_objeto_da_400_json(client):
    # Sondas 16/17 de la ronda 2: una lista no vacía es truthy y llegaba
    # a data.get(...) -> AttributeError -> 500 HTML.
    r = client.post("/api/signup", json=[{"username": "x"}])
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


def test_regresion_login_cuerpo_no_objeto_da_400_json(client):
    r = client.post("/api/login", json=["student@academy.test"])
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()
    # También una cadena JSON suelta (válida, pero no un objeto).
    r = client.post("/api/login", json="student@academy.test")
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


def test_regresion_cuerpos_no_objeto_en_verify_forgot_reset_tutor_dan_400(
        client):
    # Mismo patrón sistémico de B2 en el resto de rutas que leen JSON
    # (sondas 2/3 de la ronda 2): cada una cae en su 400 de siempre.
    for url in ("/api/verify-email", "/api/forgot-password",
                "/api/reset-password", "/api/tutor"):
        r = client.post(url, json=[1, 2, 3])
        assert r.status_code == 400, url
        assert r.is_json, url
        assert "error" in r.get_json(), url


def test_regresion_claim_cuerpo_no_objeto_da_404_json(
        client, nuevo_usuario):
    # Sonda 4 de la ronda 2: claim con cuerpo-lista -> 500; corregido,
    # el cuerpo se normaliza a {} y responde el 404 «Ruta no
    # encontrada» habitual, en JSON.
    headers, user = nuevo_usuario()
    r = client.post("/api/certificates/claim", headers=headers,
                    json=["no-soy-un-objeto"])
    assert r.status_code == 404
    assert r.is_json
    assert "error" in r.get_json()


def test_regresion_tutor_pregunta_no_cadena_da_400(client):
    # Sonda de la ronda 2: question numérica -> 500; _texto la trata
    # como '' y cae en el 400 «Escribe una pregunta para el tutor».
    r = client.post("/api/tutor", json={"question": 12345})
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


# ---------------------------------------------------------------------------
# B3 — tokens de verificación/recuperación usados como Bearer
# ---------------------------------------------------------------------------

def _signup_sin_verificar(client):
    sufijo = uuid.uuid4().hex[:10]
    email = f"regresion.{sufijo}@example.test"
    r = client.post("/api/signup", json={
        "username": f"Reg {sufijo}", "email": email,
        "password": "secret123"})
    assert r.status_code == 201, r.get_json()
    return email


def test_regresion_token_verificacion_como_bearer_da_403_json(
        client, fake_mail):
    from conftest import _token_del_correo

    _signup_sin_verificar(client)
    token = _token_del_correo(fake_mail, "Verifica tu cuenta")
    # La identidad de este token es el EMAIL, no un id: antes, int()
    # reventaba con ValueError -> 500 HTML (sondas 11/12/13).
    headers = {"Authorization": f"Bearer {token}"}
    for url in ("/api/dashboard", "/api/gamification/me", "/api/users"):
        r = client.get(url, headers=headers)
        assert r.status_code == 403, url
        assert r.is_json, url
        assert "error" in r.get_json(), url


def test_regresion_token_recuperacion_como_bearer_da_403_json(
        client, nuevo_usuario, fake_mail):
    from conftest import _token_del_correo

    headers, user = nuevo_usuario()
    r = client.post("/api/forgot-password", json={"email": user["email"]})
    assert r.status_code == 200
    token = _token_del_correo(fake_mail, "Recuperación de contraseña")
    r = client.get("/api/dashboard",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
    assert r.is_json
    assert "error" in r.get_json()


# ---------------------------------------------------------------------------
# B4/B5 — progreso: lección inexistente e is_completed no booleano
# ---------------------------------------------------------------------------

def _primera_leccion_id(client):
    return client.get("/api/lessons").get_json()[0]["id"]


def test_regresion_post_progreso_leccion_inexistente_da_404_y_get_sano(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    # Sonda 8 de la ronda 2: antes -> 201 con fila huérfana; la sonda 9
    # mostraba el GET posterior en 500 (p.lesson era None).
    r = client.post("/api/progress", headers=headers, json=[
        {"user_id": user["id"], "lesson_id": 99999}])
    assert r.status_code == 404
    assert r.is_json
    assert "error" in r.get_json()
    # El GET de progreso de la cuenta sigue sano: 200 y sin la fila.
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert r.status_code == 200
    assert r.get_json() == []


def test_regresion_put_progreso_leccion_inexistente_da_404_y_get_sano(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    r = client.put(f"/api/progress/{user['id']}/99999", headers=headers,
                   json={"is_completed": True})
    assert r.status_code == 404
    assert r.is_json
    assert "error" in r.get_json()
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert r.status_code == 200
    assert r.get_json() == []


def test_regresion_post_progreso_is_completed_no_booleano_da_400(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = _primera_leccion_id(client)
    r = client.post("/api/progress", headers=headers, json=[
        {"user_id": user["id"], "lesson_id": lid,
         "is_completed": "si"}])
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


def test_regresion_put_progreso_is_completed_no_booleano_da_400(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = _primera_leccion_id(client)
    # Sonda 15 de la ronda 2: "false" (cadena) -> 500 con el error SQL
    # y los nombres de tabla filtrados en la respuesta.
    for malo in ("false", 1):
        r = client.put(f"/api/progress/{user['id']}/{lid}",
                       headers=headers, json={"is_completed": malo})
        assert r.status_code == 400, malo
        assert r.is_json, malo
        assert "error" in r.get_json(), malo
    # Nada quedó guardado a medias: el progreso sigue sin completar.
    r = client.get(f"/api/progress/{user['id']}/{lid}", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["is_completed"] is False


def test_regresion_post_progreso_lesson_id_no_entero_da_400(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    # Sonda de la ronda 2: lesson_id "1" (cadena) -> antes pasaba la
    # validación y creaba la fila con el tipo equivocado.
    r = client.post("/api/progress", headers=headers, json=[
        {"user_id": user["id"], "lesson_id": "1"}])
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


# ---------------------------------------------------------------------------
# B6 — create_lesson con order_number no numérico
# ---------------------------------------------------------------------------

def test_regresion_create_lesson_order_number_no_numerico_da_400(
        client, admin_headers):
    modules = client.get("/api/modules").get_json()
    module_id = modules[0]["id"]
    antes = len(client.get("/api/lessons").get_json())
    # Sonda 7 de la ronda 2: "uno" -> 201 creado y el orden de
    # lecciones quedaba corrupto en silencio (afinidad de SQLite).
    r = client.post("/api/lessons", headers=admin_headers, json={
        "title": "Lección Rota", "content": "contenido",
        "module_id": module_id, "order_number": "uno"})
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()
    # Y no se creó ninguna lección con ese intento.
    despues = len(client.get("/api/lessons").get_json())
    assert despues == antes


# ---------------------------------------------------------------------------
# Ronda 3 §1 — caché del tutor: identidad frío/caliente e invalidación
# ---------------------------------------------------------------------------

_FRAG_ZORBLAX = (
    "\n\nEl zorblax cuántico es el mecanismo zorblax de esta lección: "
    "el zorblax cuántico valida cada bloque zorblax y el zorblax "
    "cuántico registra el resultado zorblax de forma inmutable."
)


def test_regresion_tutor_cache_fria_caliente_identicas_e_invalida_al_editar(
        client, app):
    # Caché fría de verdad, sea cual sea el orden de ejecución de la
    # suite: se vacía el dict de módulo antes de la primera petición.
    routes._TUTOR_CACHE.update(clave=None, docs=None, idf=None)

    pregunta_rara = {"question": "zorblax cuántico"}
    fria = client.post("/api/tutor", json=pregunta_rara)
    assert fria.status_code == 200
    assert fria.get_json()["found"] is False  # el término no existe aún
    caliente = client.post("/api/tutor", json=pregunta_rara)
    assert caliente.status_code == 200
    # Fría y caliente: cuerpos idénticos (la ronda 3 lo midió byte a
    # byte en 3 preguntas x 5 repeticiones; aquí queda fijado).
    assert caliente.get_json() == fria.get_json()

    # Lo mismo con una pregunta del temario real (found=True).
    pregunta_real = {
        "question": "¿Qué es el proof of work y cómo funciona la minería?"}
    r1 = client.post("/api/tutor", json=pregunta_real)
    r2 = client.post("/api/tutor", json=pregunta_real)
    assert r1.status_code == r2.status_code == 200
    assert r1.get_json()["found"] is True
    assert r2.get_json() == r1.get_json()

    # Editar el contenido de una lección invalida la caché: la misma
    # pregunta rara pasa a encontrar el fragmento nuevo. Sin huella de
    # invalidación, la caché serviría la respuesta vieja (found=False).
    with app.app_context():
        lecciones = db.session.execute(
            db.select(Lesson).order_by(Lesson.id)).scalars().all()
        leccion = next((l for l in lecciones if l.id == 4), lecciones[0])
        lesson_id = leccion.id
        original = leccion.content
        leccion.content = original + _FRAG_ZORBLAX
        db.session.commit()
    try:
        r = client.post("/api/tutor", json=pregunta_rara)
        assert r.status_code == 200
        body = r.get_json()
        assert body["found"] is True
        assert "zorblax" in body["answer"].lower()
    finally:
        # Restaurar el contenido y vaciar la caché: el resto de la
        # suite (test_tutor.py) debe ver la semilla intacta.
        with app.app_context():
            leccion = db.session.get(Lesson, lesson_id)
            leccion.content = original
            db.session.commit()
        routes._TUTOR_CACHE.update(clave=None, docs=None, idf=None)


# ---------------------------------------------------------------------------
# Ronda 3 §2 — N+1 corregido: el contenido devuelto no cambia
# ---------------------------------------------------------------------------

def _lecciones_de_ruta(client, titulo):
    paths = client.get("/api/learning-paths").get_json()
    path = next(p for p in paths if p["title"] == titulo)
    detalle = client.get(f"/api/learning-paths/{path['id']}").get_json()
    return path["id"], [l["id"] for m in detalle["modules"]
                         for l in m["lessons"]]


def test_regresion_modules_contenido_igual_tras_eager_loading(client):
    modules = client.get("/api/modules").get_json()
    planas = client.get("/api/lessons").get_json()
    assert len(modules) >= 5
    por_modulo = {}
    for l in planas:
        por_modulo.setdefault(l["module_id"], []).append(l)
    total = 0
    for m in modules:
        # Forma exacta de la respuesta (la semántica previa al eager).
        assert set(m.keys()) == {
            "id", "title", "level", "learning_path_id", "lessons"}
        esperadas = sorted(por_modulo.get(m["id"], []),
                           key=lambda l: l["id"])
        devueltas = sorted(m["lessons"], key=lambda l: l["id"])
        assert len(devueltas) == len(esperadas)
        for dev, esp in zip(devueltas, esperadas):
            assert dev == {"id": esp["id"], "title": esp["title"],
                           "order_number": esp["order_number"]}
        total += len(devueltas)
    assert total == len(planas)


def test_regresion_progress_contenido_igual_tras_eager_loading(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    _, lesson_ids = _lecciones_de_ruta(client, "Fundamentos de Blockchain")
    lid_a, lid_b = lesson_ids[0], lesson_ids[1]
    r = client.put(f"/api/progress/{user['id']}/{lid_a}", headers=headers,
                   json={"is_completed": True, "quiz_score": 100})
    assert r.status_code == 200
    r = client.put(f"/api/progress/{user['id']}/{lid_b}", headers=headers,
                   json={"is_completed": False, "quiz_score": 40})
    assert r.status_code == 200

    # Expectativa construida SOLO desde otros endpoints públicos: el
    # título sale del catálogo y la ruta, del módulo que la contiene.
    planas = {l["id"]: l for l in client.get("/api/lessons").get_json()}
    ruta_de = {}
    for m in client.get("/api/modules").get_json():
        for l in m["lessons"]:
            ruta_de[l["id"]] = m["learning_path_id"]
    esperado = {
        lid_a: {"lesson_id": lid_a, "lesson_title": planas[lid_a]["title"],
                "path_id": ruta_de[lid_a], "is_completed": True,
                "quiz_score": 100},
        lid_b: {"lesson_id": lid_b, "lesson_title": planas[lid_b]["title"],
                "path_id": ruta_de[lid_b], "is_completed": False,
                "quiz_score": 40},
    }
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert r.status_code == 200
    devuelto = {p["lesson_id"]: p for p in r.get_json()}
    assert devuelto == esperado


def test_regresion_certificates_mine_contenido_igual_tras_eager_loading(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    path_id, lesson_ids = _lecciones_de_ruta(
        client, "Fundamentos de Blockchain")
    for lid in lesson_ids:
        r = client.put(f"/api/progress/{user['id']}/{lid}",
                       headers=headers,
                       json={"is_completed": True, "quiz_score": 90})
        assert r.status_code == 200
    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": path_id})
    assert r.status_code == 201
    reclamado = r.get_json()

    # /certificates/mine lee c.user y c.learning_path por certificado
    # en serialize(): con el eager loading de la ronda 3 el cuerpo es
    # exactamente el mismo certificado que devolvió el claim.
    r = client.get("/api/certificates/mine", headers=headers)
    assert r.status_code == 200
    mios = r.get_json()
    assert len(mios) == 1
    assert mios[0] == reclamado
    assert mios[0]["path_title"] == "Fundamentos de Blockchain"
    assert mios[0]["holder"] == (user["username"] or user["email"])
