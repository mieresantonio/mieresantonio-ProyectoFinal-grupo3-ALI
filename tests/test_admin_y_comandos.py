"""Admin de Flask-Admin (gate) y comandos CLI de la semilla."""
import os
import sqlite3
import subprocess
import sys

from api.models import db, LearningPath, Module, Lesson, Quiz


def test_flask_admin_desactivado_por_defecto(app):
    # Sin FLASK_DEBUG=1 ni ENABLE_ADMIN=1, el CRUD sin autenticación de
    # Flask-Admin no debe quedar registrado en producción.
    assert "admin" not in app.blueprints


def test_insert_test_users_funciona(seeded):
    app = seeded
    runner = app.test_cli_runner()
    r = runner.invoke(args=["insert-test-users", "2"])
    assert r.exit_code == 0, r.output
    # Segunda corrida: no revienta ni duplica (get-or-create por correo).
    r = runner.invoke(args=["insert-test-users", "2"])
    assert r.exit_code == 0, r.output
    with app.app_context():
        from api.models import User
        n = db.session.execute(
            db.select(db.func.count()).select_from(User)
            .filter(User.email.like("test_user%@test.com"))).scalar()
    assert n == 2


def test_semilla_idempotente_y_conteos(seeded):
    app = seeded
    runner = app.test_cli_runner()
    r = runner.invoke(args=["insert-test-data"])
    assert r.exit_code == 0, r.output
    with app.app_context():
        titulos = ("Fundamentos de Blockchain",
                   "Desarrollo de Smart Contracts")
        paths = db.session.execute(
            db.select(LearningPath)
            .filter(LearningPath.title.in_(titulos))).scalars().all()
        assert len(paths) == 2
        ids = [p.id for p in paths]
        n_mod = db.session.execute(
            db.select(db.func.count()).select_from(Module)
            .filter(Module.learning_path_id.in_(ids))).scalar()
        n_les = db.session.execute(
            db.select(db.func.count()).select_from(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .filter(Module.learning_path_id.in_(ids))).scalar()
        n_quiz = db.session.execute(
            db.select(db.func.count()).select_from(Quiz)
            .join(Lesson, Quiz.lesson_id == Lesson.id)
            .join(Module, Lesson.module_id == Module.id)
            .filter(Module.learning_path_id.in_(ids))).scalar()
    assert (n_mod, n_les, n_quiz) == (5, 9, 9)


def test_semilla_sin_variable_no_reactiva_demos(seeded, monkeypatch):
    """Sin SEED_DEMO_USERS y con las cuentas demo desactivadas, la semilla
    no las reactiva ni duplica cuentas. El caso crítico es el ADMIN demo:
    nunca debe quedar activo en un despliegue público por una semilla."""
    app = seeded
    monkeypatch.delenv("SEED_DEMO_USERS", raising=False)
    emails = ("admin@academy.test", "student@academy.test")
    with app.app_context():
        from api.models import User
        for email in emails:
            u = db.session.execute(
                db.select(User).filter_by(email=email)).scalar_one()
            u.is_active = False
        db.session.commit()
        n_antes = db.session.execute(
            db.select(db.func.count()).select_from(User)).scalar()
    try:
        r = app.test_cli_runner().invoke(args=["insert-test-data"])
        assert r.exit_code == 0, r.output
        with app.app_context():
            n_despues = db.session.execute(
                db.select(db.func.count()).select_from(User)).scalar()
            estados = {
                u.email: u.is_active
                for u in db.session.execute(
                    db.select(User).filter(User.email.in_(emails))
                ).scalars()
            }
        # Ni reactivadas ni duplicadas: las cuentas quedan como estaban.
        assert estados == {"admin@academy.test": False,
                           "student@academy.test": False}
        assert n_despues == n_antes
    finally:
        # Restaurar el estado compartido de la suite pase lo que pase.
        with app.app_context():
            from api.models import User
            for email in emails:
                u = db.session.execute(
                    db.select(User).filter_by(email=email)).scalar_one()
                u.is_active = True
            db.session.commit()


_SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "src"))

_SCRIPT_DESDE_CERO = (
    "from app import app\n"
    "from api.models import db\n"
    "with app.app_context():\n"
    "    db.create_all()\n"
    "    for _ in range(2):\n"
    "        r = app.test_cli_runner().invoke(args=['insert-test-data'])\n"
    "        assert r.exit_code == 0, r.output\n"
)


def _semilla_desde_cero(tmp_path, con_admin_demo):
    """Siembra dos veces una BD nueva en un subproceso y devuelve su estado.

    Devuelve (usuarios, conteos): usuarios mapea email -> (rol, is_active)
    y conteos trae las filas de contenido y de progreso sembrado. Correr la
    semilla dos veces verifica también la idempotencia en cada modo.
    """
    db_file = tmp_path / "desde-cero.db"
    env = dict(os.environ)
    env["DATABASE_URL"] = f"sqlite:///{db_file}"
    env["FLASK_APP_KEY"] = "test-secret-key"
    env["PYTHONPATH"] = _SRC_DIR
    env.pop("FLASK_DEBUG", None)
    env.pop("ENABLE_ADMIN", None)
    if con_admin_demo:
        env["SEED_DEMO_USERS"] = "1"
    else:
        env.pop("SEED_DEMO_USERS", None)
    res = subprocess.run(
        [sys.executable, "-c", _SCRIPT_DESDE_CERO],
        env=env, capture_output=True, text=True, timeout=600,
    )
    assert res.returncode == 0, res.stderr or res.stdout
    con = sqlite3.connect(db_file)
    try:
        usuarios = {
            email: (rol, bool(activo))
            for email, rol, activo in con.execute(
                "SELECT email, role, is_active FROM users")
        }
        conteos = {
            tabla: con.execute(
                f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            for tabla in ("learning_paths", "modules", "lessons",
                          "quizzes", "user_progress")
        }
    finally:
        con.close()
    return usuarios, conteos


def test_semilla_desde_cero_sin_variable_solo_estudiante_demo(tmp_path):
    """Desde cero SIN SEED_DEMO_USERS: existe el estudiante demo (ingreso
    público, sin privilegios) y NO existe el admin demo; el contenido
    (2/5/9/9) y el progreso sembrado del estudiante quedan intactos."""
    usuarios, conteos = _semilla_desde_cero(tmp_path, con_admin_demo=False)
    assert usuarios == {"student@academy.test": ("student", True)}
    assert conteos == {
        "learning_paths": 2, "modules": 5, "lessons": 9,
        "quizzes": 9, "user_progress": 9,
    }


def test_semilla_desde_cero_con_variable_ambos_demo(tmp_path):
    """Desde cero CON SEED_DEMO_USERS=1: se crean ambos demo, como siempre
    en entornos controlados (local/pruebas)."""
    usuarios, conteos = _semilla_desde_cero(tmp_path, con_admin_demo=True)
    assert usuarios == {
        "admin@academy.test": ("admin", True),
        "student@academy.test": ("student", True),
    }
    assert conteos == {
        "learning_paths": 2, "modules": 5, "lessons": 9,
        "quizzes": 9, "user_progress": 9,
    }
