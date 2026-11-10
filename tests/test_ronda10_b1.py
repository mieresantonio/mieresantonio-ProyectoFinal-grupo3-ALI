"""Ronda 10 · Bucle 1: regresión de H-1 y cobertura de los `except`.

TAREA A — H-1 (documentado en LOG-RONDA-9-B1.md): `POST /api/modules`
sin `level` devolvía 500 en HTML porque `Module.level` es NOT NULL
(`Mapped[str]` sin `Optional`) y `create_module` no lo validaba, contra
el patrón de la API de creación (400 JSON). La revisión campo a campo
de los demás `create_*` encontró el MISMO descuido en `create_lesson`:
su guarda solo comprobaba que la clave `content` existiera, y con
`"content": null` el commit reventaba igual (500 HTML, NOT NULL en
`lessons.content`). Ambos quedan corregidos siguiendo el patrón
hermano y fijados por los tests de este fichero.

El resto de la revisión (sin corrección, con sonda en el log):
`create_learning_path` solo exige `title` y es el único NOT NULL de su
modelo (los demás son `nullable=True`); en `create_quiz`,
`questions_data: null` NO revienta (201: la columna JSON guarda el
literal JSON `null`, no un NULL de SQL); en `create_initial_progress`
el commit ya va dentro de un try que responde 500 JSON y
`is_completed: null` se guarda como el default False.

TAREA B — los tres bloques `except` que la ronda 9 dejó sin cubrir
(routes.py 651-653 y 697-699; commands.py 826-828 en la numeración
previa a esta ronda). Se cubren inyectando el fallo SOLO en
`Session.commit` y SOLO durante la petición/invocación bajo prueba,
con `monkeypatch.context()` (restauración garantizada al salir del
bloque, pase lo que pase dentro). Cada test verifica DESPUÉS, ya sin
el parche, que el estado no cambió y que la operación normal vuelve
a funcionar: si el parche contaminara la sesión compartida, esas
comprobaciones — y el resto de la suite — fallarían.
"""
from sqlalchemy.orm import Session

_MSG_COMMIT = "fallo de commit inyectado (R10)"


def _commit_roto(self, *args, **kwargs):
    raise RuntimeError(_MSG_COMMIT)


# ---------------------------------------------------------------------------
# TAREA A — create_module: level pasa a ser obligatorio (patrón hermano)
# ---------------------------------------------------------------------------

def _n_modulos(client):
    return len(client.get("/api/modules").get_json())


def test_modulo_sin_level_da_400_json_y_no_crea_nada(
        client, admin_headers):
    path_id = client.get("/api/learning-paths").get_json()[0]["id"]
    antes = _n_modulos(client)
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo R10 sin nivel", "learning_path_id": path_id})
    assert r.status_code == 400
    assert r.is_json
    assert r.get_json() == {
        "error": "Debes proporcionar título, level y learning_path_id"}
    assert _n_modulos(client) == antes


def test_modulo_level_nulo_da_400_json(client, admin_headers):
    path_id = client.get("/api/learning-paths").get_json()[0]["id"]
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo R10 nivel nulo", "level": None,
        "learning_path_id": path_id})
    assert r.status_code == 400
    assert r.is_json
    assert r.get_json() == {
        "error": "Debes proporcionar título, level y learning_path_id"}


def test_modulo_level_vacio_o_no_cadena_da_400(client, admin_headers):
    # level se valida con _texto, como el título en todos los create_*:
    # cadena vacía y no-cadena también son 400, no un 201 con basura.
    path_id = client.get("/api/learning-paths").get_json()[0]["id"]
    for malo in ("", 123):
        r = client.post("/api/modules", headers=admin_headers, json={
            "title": "Módulo R10 nivel malo", "level": malo,
            "learning_path_id": path_id})
        assert r.status_code == 400, malo
        assert "error" in r.get_json()


def test_modulo_sin_level_y_ruta_inexistente_da_400_no_404(
        client, admin_headers):
    # Orden del patrón hermano: primero la validación (400), después la
    # existencia del padre (404). Sin level, ni se llega a buscar la ruta.
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo R10 orden", "learning_path_id": 99999})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_modulo_con_level_sigue_creando_201(client, admin_headers):
    path_id = client.get("/api/learning-paths").get_json()[0]["id"]
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo R10 correcto", "level": "Principiante",
        "learning_path_id": path_id})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Módulo R10 correcto"


# ---------------------------------------------------------------------------
# TAREA A — create_lesson: el mismo descuido con content null
# ---------------------------------------------------------------------------

def _n_lecciones(client):
    return len(client.get("/api/lessons").get_json())


def test_leccion_content_nulo_da_400_json_y_no_crea_nada(
        client, admin_headers):
    module_id = client.get("/api/modules").get_json()[0]["id"]
    antes = _n_lecciones(client)
    r = client.post("/api/lessons", headers=admin_headers, json={
        "title": "Lección R10 nula", "content": None,
        "module_id": module_id, "order_number": 99})
    assert r.status_code == 400
    assert r.is_json
    assert r.get_json() == {
        "error": "Debes proporcionar título, contenido, module_id "
                 "y order_number"}
    assert _n_lecciones(client) == antes


def test_leccion_sin_content_da_400_json(client, admin_headers):
    # Par del anterior: la clave ausente ya daba 400 antes de la ronda;
    # se fija aquí para que ausente y null queden gemelos.
    module_id = client.get("/api/modules").get_json()[0]["id"]
    r = client.post("/api/lessons", headers=admin_headers, json={
        "title": "Lección R10 sin contenido",
        "module_id": module_id, "order_number": 99})
    assert r.status_code == 400
    assert r.get_json() == {
        "error": "Debes proporcionar título, contenido, module_id "
                 "y order_number"}


# ---------------------------------------------------------------------------
# TAREA B — except de POST /progress (rollback + 500 al fallar el commit)
# ---------------------------------------------------------------------------

def test_post_progress_commit_falla_da_500_json_y_no_contamina(
        client, nuevo_usuario, monkeypatch):
    headers, user = nuevo_usuario()
    lid = client.get("/api/lessons").get_json()[0]["id"]
    payload = [{"user_id": user["id"], "lesson_id": lid,
                "is_completed": True, "quiz_score": 80}]

    with monkeypatch.context() as m:
        m.setattr(Session, "commit", _commit_roto)
        r = client.post("/api/progress", headers=headers, json=payload)
    assert r.status_code == 500
    assert r.is_json
    assert r.get_json() == {"error": _MSG_COMMIT}

    # El rollback del except dejó la BD como estaba (sin la fila) y la
    # sesión sana: la misma petición, ya sin parche, crea el progreso.
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert r.get_json() == []
    r = client.post("/api/progress", headers=headers, json=payload)
    assert r.status_code == 201
    r = client.get(f"/api/progress/{user['id']}", headers=headers)
    assert len(r.get_json()) == 1
    assert r.get_json()[0]["quiz_score"] == 80


# ---------------------------------------------------------------------------
# TAREA B — except de PUT /progress (rollback + 500 al fallar el commit)
# ---------------------------------------------------------------------------

def test_put_progress_commit_falla_da_500_json_y_no_contamina(
        client, nuevo_usuario, monkeypatch):
    headers, user = nuevo_usuario()
    lid = client.get("/api/lessons").get_json()[0]["id"]
    url = f"/api/progress/{user['id']}/{lid}"

    # Estado base conocido, creado SIN parche: quiz 10, sin completar.
    r = client.put(url, headers=headers,
                   json={"is_completed": False, "quiz_score": 10})
    assert r.status_code == 200

    with monkeypatch.context() as m:
        m.setattr(Session, "commit", _commit_roto)
        r = client.put(url, headers=headers,
                       json={"is_completed": True, "quiz_score": 99})
    assert r.status_code == 500
    assert r.is_json
    assert r.get_json() == {"error": _MSG_COMMIT}

    # Nada del intento fallido quedó guardado…
    r = client.get(url, headers=headers)
    assert r.get_json() == {
        "lesson_id": lid, "is_completed": False, "quiz_score": 10}
    # …y la sesión compartida sigue operativa tras el rollback.
    r = client.put(url, headers=headers, json={"quiz_score": 20})
    assert r.status_code == 200
    r = client.get(url, headers=headers)
    assert r.get_json()["quiz_score"] == 20


# ---------------------------------------------------------------------------
# TAREA B — except de insert_test_data en commands.py (rollback + raise)
# ---------------------------------------------------------------------------

def test_insert_test_data_commit_falla_relanta_y_no_contamina(
        app, client, monkeypatch):
    def conteos():
        return (
            len(client.get("/api/learning-paths").get_json()),
            _n_modulos(client),
            _n_lecciones(client),
        )

    antes = conteos()
    with monkeypatch.context() as m:
        m.setattr(Session, "commit", _commit_roto)
        result = app.test_cli_runner().invoke(args=["insert-test-data"])
    # El except de la semilla hace rollback y RELANZA: el runner recoge
    # exactamente la excepción inyectada y el comando sale con error.
    assert result.exit_code != 0
    assert isinstance(result.exception, RuntimeError)
    assert _MSG_COMMIT in str(result.exception)

    # La semilla es get-or-create e idempotente y su intento fallido se
    # revirtió entero: el catálogo compartido queda como estaba y la
    # API sigue respondiendo (la sesión no quedó contaminada).
    assert conteos() == antes
    r = client.post("/api/login", json={
        "email": "student@academy.test", "password": "Student123!"})
    assert r.status_code == 200
