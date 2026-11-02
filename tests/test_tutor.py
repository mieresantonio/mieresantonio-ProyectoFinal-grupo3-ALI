"""Tutor de Blockali: responde solo desde las lecciones, con fuentes."""


def test_pregunta_vacia_o_larga_da_400(client):
    r = client.post("/api/tutor", json={"question": ""})
    assert r.status_code == 400
    r = client.post("/api/tutor", json={"question": "   "})
    assert r.status_code == 400
    r = client.post("/api/tutor", json={"question": "x" * 501})
    assert r.status_code == 400
    r = client.post("/api/tutor", data="sin json",
                    content_type="text/plain")
    assert r.status_code == 400


def test_pregunta_en_temario_encuentra_fuente(client):
    r = client.post("/api/tutor", json={
        "question": "¿Qué es el proof of work y cómo funciona la minería?"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["found"] is True
    assert body["sources"]
    assert body["sources"][0]["lesson_title"] == "Proof of Work"
    assert body["sources"][0]["path_title"] == "Fundamentos de Blockchain"
    assert body["answer"]


def test_pregunta_fuera_de_temario_lo_dice(client):
    r = client.post("/api/tutor", json={
        "question": "¿Cómo preparo una pizza napolitana en horno de leña?"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["found"] is False
    assert "no aparece en las lecciones" in body["answer"]
