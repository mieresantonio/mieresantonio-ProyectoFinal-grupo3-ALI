"""Ronda 11 · Bucle 1: `is_completed: null` en PUT /progress.

Observación de la ronda 10 (LOG-RONDA-10-B1.md §4): en
`update_progress` (PUT) un `is_completed: null` superaba la guarda
(solo rechaza no-booleanos NO nulos) y la asignación
`progress.is_completed = body.get(...)` escribía None sobre la fila.

La sonda de esta ronda (usuario nuevo, sin progreso sembrado —
la semilla crea filas para el student demo y contaminaba los casos
de creación) precisó el alcance ANTES de la corrección:

- POST null creando: 201 y la fila queda con False (el default del
  modelo): null equivale al default, idéntico a omitir la clave.
- POST null sobre fila existente: POST salta las existentes (201 sin
  tocarlas): null equivale a «sin cambio».
- PUT null creando: 200 por casualidad (el INSERT aplica el mismo
  default False).
- PUT null sobre fila EXISTENTE: **500 JSON** con
  `IntegrityError: NOT NULL constraint failed:
  user_progress.is_completed` y el SQL filtrado en el cuerpo — la
  columna es `Mapped[bool]` sin Optional (NOT NULL) y un UPDATE a
  None no tiene representación. La fila quedaba intacta por el
  rollback del except, pero la respuesta era un 500.

Corrección (misma semántica que POST, coherencia interna): solo se
asigna `is_completed` cuando viene un booleano de verdad; null es
«sin cambio» en una fila existente y el default False al crear.
La guarda de la ronda 2 no cambia: un no-booleano no nulo sigue
siendo 400. `quiz_score` no se toca: su columna SÍ es nullable y
null es ahí un valor legítimo también en POST.
"""


def _lid(client):
    return client.get("/api/lessons").get_json()[0]["id"]


def _get(client, headers, uid, lid):
    r = client.get(f"/api/progress/{uid}/{lid}", headers=headers)
    assert r.status_code == 200
    return r.get_json()


# ---------------------------------------------------------------------------
# La semántica de referencia: POST con null (sin cambios en esta ronda)
# ---------------------------------------------------------------------------

def test_post_progress_is_completed_nulo_se_guarda_como_default(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = _lid(client)
    r = client.post("/api/progress", headers=headers, json=[
        {"user_id": user["id"], "lesson_id": lid, "is_completed": None}])
    assert r.status_code == 201
    assert _get(client, headers, user["id"], lid) == {
        "lesson_id": lid, "is_completed": False, "quiz_score": 0}


# ---------------------------------------------------------------------------
# PUT con null: el caso que daba 500 y sus gemelos
# ---------------------------------------------------------------------------

def test_put_progress_is_completed_nulo_sobre_existente_es_sin_cambio(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = _lid(client)
    url = f"/api/progress/{user['id']}/{lid}"
    r = client.put(url, headers=headers,
                   json={"is_completed": True, "quiz_score": 55})
    assert r.status_code == 200

    # ANTES: 500 JSON con el IntegrityError y el SQL en el cuerpo.
    r = client.put(url, headers=headers, json={"is_completed": None})
    assert r.status_code == 200
    assert r.is_json
    assert r.get_json() == {"message": "Progress updated"}
    # Sin cambio: ni el flag ni la nota se tocaron.
    assert _get(client, headers, user["id"], lid) == {
        "lesson_id": lid, "is_completed": True, "quiz_score": 55}


def test_put_progress_nulo_no_bloquea_otros_campos(
        client, nuevo_usuario):
    # null solo ignora SU campo: un quiz_score válido en el mismo
    # cuerpo sí se aplica, y el is_completed existente se conserva.
    headers, user = nuevo_usuario()
    lid = _lid(client)
    url = f"/api/progress/{user['id']}/{lid}"
    r = client.put(url, headers=headers,
                   json={"is_completed": False, "quiz_score": 10})
    assert r.status_code == 200
    r = client.put(url, headers=headers,
                   json={"is_completed": None, "quiz_score": 77})
    assert r.status_code == 200
    assert _get(client, headers, user["id"], lid) == {
        "lesson_id": lid, "is_completed": False, "quiz_score": 77}


def test_put_progress_is_completed_nulo_creando_aplica_default(
        client, nuevo_usuario):
    headers, user = nuevo_usuario()
    lid = _lid(client)
    r = client.put(f"/api/progress/{user['id']}/{lid}", headers=headers,
                   json={"is_completed": None})
    assert r.status_code == 200
    assert _get(client, headers, user["id"], lid) == {
        "lesson_id": lid, "is_completed": False, "quiz_score": None}


def test_put_progress_is_completed_no_booleano_sigue_dando_400(
        client, nuevo_usuario):
    # Control: la guarda de la ronda 2 queda intacta — null se acepta
    # con la semántica de arriba, pero "false"/1 siguen siendo 400.
    headers, user = nuevo_usuario()
    lid = _lid(client)
    for malo in ("false", 1):
        r = client.put(f"/api/progress/{user['id']}/{lid}",
                       headers=headers, json={"is_completed": malo})
        assert r.status_code == 400, malo
        assert r.is_json, malo
        assert "error" in r.get_json(), malo
