"""Certificados verificables: reclamar, listar y verificar en público."""
import re

from test_progreso_gamificacion import _lecciones_ruta


def _completar_ruta(client, headers, user_id, titulo, score=90):
    path_id, lesson_ids = _lecciones_ruta(client, titulo)
    for lid in lesson_ids:
        r = client.put(f"/api/progress/{user_id}/{lid}", headers=headers,
                       json={"is_completed": True, "quiz_score": score})
        assert r.status_code == 200
    return path_id


def test_reclamar_sin_completar_da_400(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    path_id, _ = _lecciones_ruta(client, "Fundamentos de Blockchain")
    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": path_id})
    assert r.status_code == 400
    body = r.get_json()
    assert body["lessons_completed"] == 0
    assert body["lessons_total"] == 5


def test_flujo_completo_certificado(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    path_id = _completar_ruta(
        client, headers, user["id"], "Fundamentos de Blockchain")

    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": path_id})
    assert r.status_code == 201
    cert = r.get_json()
    assert re.fullmatch(r"BK-[0-9A-F]{5}-[0-9A-F]{5}-[0-9A-F]{5}",
                        cert["code"])
    assert cert["path_id"] == path_id

    # Reclamar de nuevo devuelve el mismo certificado (200, no duplica).
    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": path_id})
    assert r.status_code == 200
    assert r.get_json()["code"] == cert["code"]

    mios = client.get("/api/certificates/mine",
                      headers=headers).get_json()
    assert len(mios) == 1
    assert mios[0]["code"] == cert["code"]

    # Verificación pública, sin token.
    r = client.get(f"/api/certificates/verify/{cert['code']}")
    assert r.status_code == 200
    body = r.get_json()
    assert body["valid"] is True
    assert body["path"] == "Fundamentos de Blockchain"
    r = client.get("/api/certificates/verify/BK-XXXXX-XXXXX-XXXXX")
    assert r.status_code == 404
    assert r.get_json()["valid"] is False


def test_certificado_quiz_suspendido_bloquea(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    path_id = _completar_ruta(
        client, headers, user["id"], "Desarrollo de Smart Contracts",
        score=50)
    r = client.post("/api/certificates/claim", headers=headers,
                    json={"path_id": path_id})
    assert r.status_code == 400
    assert r.get_json()["quizzes_pending"]
