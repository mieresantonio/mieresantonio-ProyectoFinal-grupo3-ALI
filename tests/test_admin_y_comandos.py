"""Admin de Flask-Admin (gate) y comandos CLI de la semilla."""
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
