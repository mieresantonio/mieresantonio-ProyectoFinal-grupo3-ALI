"""Catálogo público: rutas, módulos, lecciones y quizzes."""


def test_lista_rutas_forma_y_contenido(client):
    r = client.get("/api/learning-paths")
    assert r.status_code == 200
    paths = r.get_json()
    assert len(paths) >= 2
    esperadas = {"id", "title", "image_url", "description",
                 "time_required", "level", "number_of_modules", "modules"}
    for p in paths:
        assert esperadas <= set(p.keys())
    titulos = {p["title"] for p in paths}
    assert "Fundamentos de Blockchain" in titulos
    assert "Desarrollo de Smart Contracts" in titulos


def test_detalle_ruta_con_modulos_y_lecciones(client):
    paths = client.get("/api/learning-paths").get_json()
    fund = next(p for p in paths if p["title"] == "Fundamentos de Blockchain")
    r = client.get(f"/api/learning-paths/{fund['id']}")
    assert r.status_code == 200
    detalle = r.get_json()
    assert detalle["number_of_modules"] == 2
    assert len(detalle["modules"]) == 2
    for m in detalle["modules"]:
        assert m["lessons"], "cada módulo de la semilla trae lecciones"


def test_404_en_json(client):
    for url in ("/api/learning-paths/99999", "/api/modules/99999",
                "/api/lessons/99999", "/api/quizzes/99999"):
        r = client.get(url)
        assert r.status_code == 404, url
        assert "error" in r.get_json(), url


def test_modulos_lecciones_y_quiz(client):
    modules = client.get("/api/modules").get_json()
    assert len(modules) >= 5
    lessons = client.get("/api/lessons").get_json()
    assert len(lessons) >= 9
    primera = lessons[0]
    detalle = client.get(f"/api/lessons/{primera['id']}").get_json()
    assert detalle["content"]
    assert detalle["module_lessons"]
    quiz = client.get(f"/api/quizzes/{primera['id']}")
    assert quiz.status_code == 200
    assert len(quiz.get_json()["questions"]) == 4
