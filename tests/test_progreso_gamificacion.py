"""Progreso del usuario, permisos y gamificación."""
from api.models import db, UserProgress


def _lecciones_ruta(client, titulo):
    paths = client.get("/api/learning-paths").get_json()
    path = next(p for p in paths if p["title"] == titulo)
    detalle = client.get(f"/api/learning-paths/{path['id']}").get_json()
    return path["id"], [l["id"] for m in detalle["modules"]
                         for l in m["lessons"]]


def test_inicializar_progreso_sin_duplicados(client, nuevo_usuario, app):
    headers, user = nuevo_usuario()
    _, lesson_ids = _lecciones_ruta(client, "Fundamentos de Blockchain")
    body = [{"user_id": user["id"], "lesson_id": lid}
            for lid in lesson_ids]
    r = client.post("/api/progress", headers=headers, json=body)
    assert r.status_code == 201
    # Repetir la inicialización NO debe duplicar filas (la XP sumaba doble).
    r = client.post("/api/progress", headers=headers, json=body)
    assert r.status_code == 201
    with app.app_context():
        n = db.session.execute(
            db.select(db.func.count()).select_from(UserProgress)
            .filter_by(user_id=user["id"])).scalar()
    assert n == len(lesson_ids)


def test_progreso_validaciones(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    r = client.post("/api/progress", headers=headers, json=[1, 2])
    assert r.status_code == 400
    r = client.post("/api/progress", headers=headers,
                    json=[{"user_id": user["id"]}])
    assert r.status_code == 400
    r = client.post("/api/progress", headers=headers,
                    json=[{"user_id": user["id"] + 999, "lesson_id": 1}])
    assert r.status_code == 403
    r = client.post("/api/progress", headers=headers, json={"no": "lista"})
    assert r.status_code == 400


def test_completar_leccion_y_gamificacion(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    _, lesson_ids = _lecciones_ruta(client, "Fundamentos de Blockchain")
    lid = lesson_ids[0]
    r = client.put(f"/api/progress/{user['id']}/{lid}", headers=headers,
                   json={"is_completed": True, "quiz_score": 100})
    assert r.status_code == 200
    progreso = client.get(
        f"/api/progress/{user['id']}/{lid}", headers=headers).get_json()
    assert progreso["is_completed"] is True
    assert progreso["quiz_score"] == 100
    gami = client.get("/api/gamification/me", headers=headers).get_json()
    assert gami["lessons_completed"] == 1
    assert gami["quizzes_passed"] == 1
    assert gami["xp"] == 200  # 100 de la lección + 100 del quiz
    assert gami["level_name"] == "Explorador"


def test_quiz_score_fuera_de_rango_da_400(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    _, lesson_ids = _lecciones_ruta(client, "Fundamentos de Blockchain")
    lid = lesson_ids[0]
    for malo in (99999, -5, "cien", True):
        r = client.put(f"/api/progress/{user['id']}/{lid}",
                       headers=headers, json={"quiz_score": malo})
        assert r.status_code == 400, malo
    r = client.put(f"/api/progress/{user['id']}/{lid}", headers=headers,
                   json=[1, 2])
    assert r.status_code == 400


def test_progreso_ajeno_prohibido(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    otros, otro = nuevo_usuario()
    r = client.get(f"/api/progress/{otro['id']}", headers=headers)
    assert r.status_code == 403
    r = client.put(f"/api/progress/{otro['id']}/1", headers=headers,
                   json={"is_completed": True})
    assert r.status_code == 403


def test_perfil_de_usuario_solo_dueno_o_admin(
        client, nuevo_usuario, admin_headers):
    headers, user = nuevo_usuario()
    _, otro = nuevo_usuario()
    r = client.get(f"/api/users/{user['id']}", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["email"] == user["email"]
    r = client.get(f"/api/users/{otro['id']}", headers=headers)
    assert r.status_code == 403
    r = client.get(f"/api/users/{otro['id']}", headers=admin_headers)
    assert r.status_code == 200
    r = client.get("/api/users/99999", headers=admin_headers)
    assert r.status_code == 404


def test_lista_usuarios_solo_admin(client, student_headers, admin_headers):
    r = client.get("/api/users", headers=student_headers)
    assert r.status_code == 403
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200
    assert any(u["email"] == "admin@academy.test" for u in r.get_json())
