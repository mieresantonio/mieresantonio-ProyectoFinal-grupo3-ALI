"""Autenticación: registro, verificación, login y recuperación."""


def test_signup_campos_nulos_no_dan_500(client):
    # username es opcional (nullable en el modelo): null se trata como ''
    # y el registro procede; antes reventaba con AttributeError (500 HTML).
    r = client.post("/api/signup", json={
        "username": None, "email": "n@n.test", "password": "secret1"})
    assert r.status_code == 201
    assert "message" in r.get_json()
    # email null sí es un 400 JSON (sin correo válido no hay registro).
    r = client.post("/api/signup", json={
        "username": "x", "email": None, "password": "secret1"})
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_signup_validaciones_basicas(client):
    r = client.post("/api/signup", json={
        "username": "x", "email": "no-es-correo", "password": "secret1"})
    assert r.status_code == 400
    r = client.post("/api/signup", json={
        "username": "x", "email": "ok@ok.test", "password": "123"})
    assert r.status_code == 400
    r = client.post("/api/signup", data="no json",
                    content_type="text/plain")
    assert r.status_code == 400


def test_login_credenciales_invalidas(client):
    r = client.post("/api/login", json={
        "email": "student@academy.test", "password": "incorrecta"})
    assert r.status_code == 401
    r = client.post("/api/login", json={
        "email": "nadie@example.test", "password": "loquesea1"})
    assert r.status_code == 401


def test_login_sin_verificar_da_403(client, fake_mail):
    r = client.post("/api/signup", json={
        "username": "Sin Verificar", "email": "sin.verificar@example.test",
        "password": "secret123"})
    assert r.status_code == 201
    r = client.post("/api/login", json={
        "email": "sin.verificar@example.test", "password": "secret123"})
    assert r.status_code == 403


def test_verify_token_invalido(client):
    r = client.post("/api/verify-email", json={"token": "token-malo"})
    assert r.status_code == 400
    assert "error" in r.get_json()
    r = client.post("/api/verify-email", json={})
    assert r.status_code == 400


def test_signup_duplicado_activo_da_400(client, nuevo_usuario):
    headers, user = nuevo_usuario()
    r = client.post("/api/signup", json={
        "username": "Otro", "email": user["email"], "password": "secret123"})
    assert r.status_code == 400


def test_recuperacion_de_contrasena(client, nuevo_usuario, fake_mail):
    from conftest import _token_del_correo

    headers, user = nuevo_usuario()
    r = client.post("/api/forgot-password", json={"email": user["email"]})
    assert r.status_code == 200
    # Correo inexistente: misma respuesta genérica (no revela registros).
    r = client.post("/api/forgot-password", json={
        "email": "fantasma@example.test"})
    assert r.status_code == 200

    token = _token_del_correo(fake_mail, "Recuperación de contraseña")
    r = client.post("/api/reset-password", json={
        "token": token, "password": "nuevaClave9"})
    assert r.status_code == 200
    r = client.post("/api/login", json={
        "email": user["email"], "password": "secret123"})
    assert r.status_code == 401
    r = client.post("/api/login", json={
        "email": user["email"], "password": "nuevaClave9"})
    assert r.status_code == 200
