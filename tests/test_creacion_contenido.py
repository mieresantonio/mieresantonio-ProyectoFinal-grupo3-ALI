"""Creación de contenido: solo admin, con validación (antes: 500 HTML)."""


def test_admin_crea_ruta_modulo_leccion_y_quiz(client, admin_headers):
    r = client.post("/api/learning-paths", headers=admin_headers, json={
        "title": "Ruta de Prueba", "description": "d",
        "time_required": "1 hora", "level": "Principiante"})
    assert r.status_code == 201
    path_id = r.get_json()["id"]

    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Módulo de Prueba", "level": "Principiante",
        "learning_path_id": path_id})
    assert r.status_code == 201
    module_id = r.get_json()["id"]

    r = client.post("/api/lessons", headers=admin_headers, json={
        "title": "Lección de Prueba", "content": "Contenido de prueba",
        "module_id": module_id, "order_number": 1})
    assert r.status_code == 201
    lesson_id = r.get_json()["id"]

    r = client.post("/api/quizzes", headers=admin_headers, json={
        "lesson_id": lesson_id, "questions_data": []})
    assert r.status_code == 201

    detalle = client.get(f"/api/learning-paths/{path_id}").get_json()
    assert detalle["modules"][0]["lessons"][0]["id"] == lesson_id


def test_estudiante_no_puede_crear_contenido(client, student_headers):
    for url, payload in (
        ("/api/learning-paths", {"title": "X"}),
        ("/api/modules", {"title": "X", "learning_path_id": 1}),
        ("/api/lessons", {"title": "X", "content": "c",
                          "module_id": 1, "order_number": 1}),
        ("/api/quizzes", {"lesson_id": 1, "questions_data": []}),
    ):
        r = client.post(url, headers=student_headers, json=payload)
        assert r.status_code == 403, url
        assert "error" in r.get_json(), url


def test_crear_sin_token_da_401(client):
    r = client.post("/api/learning-paths", json={"title": "X"})
    assert r.status_code == 401


def test_crear_con_datos_invalidos_da_400_no_500(client, admin_headers):
    r = client.post("/api/learning-paths", headers=admin_headers, json={})
    assert r.status_code == 400
    assert "error" in r.get_json()
    r = client.post("/api/modules", headers=admin_headers,
                    json={"title": "Sin ruta"})
    assert r.status_code == 400
    r = client.post("/api/lessons", headers=admin_headers, json={})
    assert r.status_code == 400
    r = client.post("/api/quizzes", headers=admin_headers, json={})
    assert r.status_code == 400


def test_crear_con_padre_inexistente_da_404(client, admin_headers):
    r = client.post("/api/modules", headers=admin_headers, json={
        "title": "Huérfano", "learning_path_id": 99999})
    assert r.status_code == 404
    r = client.post("/api/lessons", headers=admin_headers, json={
        "title": "Huérfana", "content": "c", "module_id": 99999,
        "order_number": 1})
    assert r.status_code == 404
    r = client.post("/api/quizzes", headers=admin_headers, json={
        "lesson_id": 99999, "questions_data": []})
    assert r.status_code == 404
