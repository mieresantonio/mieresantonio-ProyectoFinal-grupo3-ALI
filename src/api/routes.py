import hashlib
import os
import re
from datetime import timedelta, datetime

from flask import request, jsonify, Blueprint
from flask_cors import CORS
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    decode_token,
)
from flask_mail import Message

from api.models import db, User, UserType, LearningPath, Module, Lesson, Quiz, UserProgress, Certificate
from api.utils import APIException
from api.mail import mail

api = Blueprint('api', __name__)
CORS(api)

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'


# ============================================================================
# AUTENTICACIÓN (registro + verificación de correo)
# ============================================================================

@api.route('/signup', methods=['POST'])
def handle_signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la petición inválido"}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Debes proporcionar un correo electrónico válido"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    existing = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if existing and existing.is_active:
        return jsonify({"error": "El correo ya está registrado y activo. Inicia sesión."}), 400

    if existing and not existing.is_active:
        existing.username = username
        existing.set_password(password)
        user = existing
    else:
        user = User(email=email, username=username,
                    is_active=False, role=UserType.student)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()

    token = create_access_token(
        identity=user.email,
        expires_delta=timedelta(hours=24),
        additional_claims={"type": "verify_email"}
    )
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/verify-email?token={token}"

    try:
        msg = Message(
            subject="Verifica tu cuenta en ALI",
            recipients=[user.email],
            html=f"""
            <div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;
                        padding:32px 24px;line-height:1.6;color:#212529">
              <h2 style="margin:0 0 20px 0">¡Hola{f', {username}' if username else ''}!</h2>
              <p style="margin:0 0 24px 0">
                Gracias por registrarte en ALI. Confirma tu correo para activar tu cuenta:
              </p>
              <p style="margin:0 0 24px 0">
                <a href="{verification_link}"
                   style="display:inline-block;background:#0d6efd;color:#fff;
                          padding:14px 32px;border-radius:6px;text-decoration:none;
                          font-weight:bold">Verificar mi cuenta</a>
              </p>
              <p style="margin:0 0 8px 0;color:#6c757d;font-size:14px">
                Este enlace vence en 24 horas.
              </p>
              <p style="margin:0;color:#6c757d;font-size:14px">
                Si no fuiste tú, ignora este correo de forma segura.
              </p>
            </div>
            """
        )
        mail.send(msg)
    except Exception as e:
        print("Error enviando correo de verificación:", str(e))
        return jsonify({
            "message": "Usuario registrado, pero hubo un error al enviar el correo.",
            "error": str(e)
        }), 500

    return jsonify({"message": "Usuario registrado con éxito. Revisa tu correo para verificar tu cuenta."}), 201


@api.route('/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la petición inválido"}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not user.is_active:
        return jsonify({"error": "Debes verificar tu correo antes de iniciar sesión."}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.serialize()}), 200


@api.route('/verify-email', methods=['POST'])
def handle_verify_email():
    data = request.get_json()
    token = data.get('token') if data else None
    if not token:
        return jsonify({"error": "No se proporcionó ningún token de verificación."}), 400

    try:
        decoded = decode_token(token)
        if decoded.get('type') != 'verify_email':
            return jsonify({"error": "Tipo de token inválido"}), 400

        email = decoded.get('sub')
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        if user.is_active:
            return jsonify({"message": "Tu cuenta ya se encuentra verificada."}), 200

        user.is_active = True
        db.session.commit()
        return jsonify({"message": "¡Cuenta verificada exitosamente! Ya puedes iniciar sesión."}), 200

    except Exception as e:
        return jsonify({"error": "El enlace de verificación es inválido o ha expirado.", "detail": str(e)}), 400


@api.route('/forgot-password', methods=['POST'])
def handle_forgot_password():
    data = request.get_json()
    email = data.get('email', '').strip().lower() if data else ''

    if not email:
        return jsonify({"error": "Debes proporcionar un correo electrónico."}), 400

    user = db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()

    # Por seguridad, respondemos igual exista o no el correo (no revelamos
    # si un email está registrado).
    generic_message = "Si el correo existe, hemos enviado las instrucciones para restablecer tu contraseña."

    if not user:
        return jsonify({"message": generic_message}), 200

    token = create_access_token(
        identity=user.email,
        expires_delta=timedelta(hours=1),
        additional_claims={"type": "reset_password"}
    )
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    try:
        msg = Message(
            subject="Recuperación de contraseña - ALI",
            recipients=[user.email],
            html=f"""
            <div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;
                        padding:32px 24px;line-height:1.6;color:#212529">
              <h2 style="margin:0 0 20px 0">Hola{f', {user.username}' if user.username else ''},</h2>
              <p style="margin:0 0 24px 0">
                Recibimos una solicitud para restablecer la contraseña de tu cuenta.
                Haz clic en el siguiente botón para continuar:
              </p>
              <p style="margin:0 0 24px 0">
                <a href="{reset_link}"
                   style="display:inline-block;background:#0d6efd;color:#fff;
                          padding:14px 32px;border-radius:6px;text-decoration:none;
                          font-weight:bold">Restablecer contraseña</a>
              </p>
              <p style="margin:0 0 8px 0;color:#6c757d;font-size:14px">
                Este enlace expirará en 1 hora.
              </p>
              <p style="margin:0;color:#6c757d;font-size:14px">
                Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
              </p>
            </div>
            """
        )
        mail.send(msg)
    except Exception as e:
        print("Error enviando correo de recuperación:", str(e))

    return jsonify({"message": generic_message}), 200


@api.route('/reset-password', methods=['POST'])
def handle_reset_password():
    data = request.get_json()
    token = data.get('token') if data else None
    new_password = data.get('password') if data else None

    if not token or not new_password:
        return jsonify({"error": "Faltan datos para restablecer la contraseña."}), 400
    if len(new_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    try:
        decoded = decode_token(token)
        if decoded.get('type') != 'reset_password':
            return jsonify({"error": "Tipo de token inválido"}), 400

        email = decoded.get('sub')
        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Tu contraseña ha sido restablecida con éxito. Ya puedes iniciar sesión."}), 200

    except Exception as e:
        return jsonify({"error": "El enlace es inválido o ha expirado.", "detail": str(e)}), 400


# ============================================================================
# RUTAS ORIGINALES DEL PROYECTO (sin cambios)
# ============================================================================

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

# ---- USERS ----


@api.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = db.session.get(User, int(get_jwt_identity()))
    if not current_user or current_user.role != UserType.admin:
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([u.serialize() for u in users]), 200


@api.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200

# ---- LEARNING PATHS ----


@api.route('/learning-paths', methods=['GET'])
def get_learning_paths():
    paths = db.session.execute(db.select(LearningPath)).scalars().all()
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "image_url": p.image_url,
        "description": p.description,
        "time_required": p.time_required,
        "level": p.level,
        "number_of_modules": len(p.modules),
        "modules": [{"id": m.id, "title": m.title} for m in p.modules]} for p in paths]), 200


@api.route('/learning-paths/<int:path_id>', methods=['GET'])
def get_learning_path(path_id):
    path = db.session.get(LearningPath, path_id)
    if not path:
        return jsonify({"error": "Learning path not found"}), 404
    return jsonify({
        "id": path.id,
        "title": path.title,
        "image_url": path.image_url,
        "description": path.description,
        "time_required": path.time_required,
        "level": path.level,
        "number_of_modules": len(path.modules),
        "modules": [{"id": m.id, "title": m.title, "lessons": [{"id": l.id, "title": l.title} for l in m.lessons]} for m in path.modules]}), 200


@api.route('/learning-paths', methods=['POST'])
@jwt_required()
def create_learning_path():
    body = request.json
    path = LearningPath(title=body["title"], image_url=body.get("image_url"), description=body.get(
        "description"), time_required=body.get("time_required"), level=body.get("level"))
    db.session.add(path)
    db.session.commit()
    return jsonify({"id": path.id, "title": path.title, "image_url": path.image_url, "description": path.description, "time_required": path.time_required, "level": path.level}), 201

# ---- MODULES ----


@api.route('/modules', methods=['GET'])
def get_modules():
    modules = db.session.execute(db.select(Module)).scalars().all()
    return jsonify([{
        "id": m.id,
        "title": m.title,
        "level": m.level,
        "learning_path_id": m.learning_path_id,
        "lessons": [{"id": l.id, "title": l.title, "order_number": l.order_number} for l in m.lessons]} for m in modules]), 200


@api.route('/modules/<int:module_id>', methods=['GET'])
def get_module(module_id):
    module = db.session.get(Module, module_id)
    if not module:
        return jsonify({"error": "Module not found"}), 404
    return jsonify({"id": module.id, "title": module.title, "level": module.level}), 200


@api.route('/modules', methods=['POST'])
@jwt_required()
def create_module():
    body = request.json
    module = Module(title=body["title"], level=body.get(
        "level"), learning_path_id=body["learning_path_id"])
    db.session.add(module)
    db.session.commit()
    return jsonify({"id": module.id, "title": module.title, "lessons": []}), 201

# ---- LESSONS ----


@api.route('/lessons', methods=['GET'])
def get_lessons():
    lessons = db.session.execute(db.select(Lesson)).scalars().all()
    return jsonify([{"id": l.id, "title": l.title, "module_id": l.module_id, "order_number": l.order_number} for l in lessons]), 200


@api.route('/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    return jsonify({
        "id": lesson.id,
        "title": lesson.title,
        "module_id": lesson.module_id,
        "content": lesson.content,
        "order_number": lesson.order_number,
        "module_lessons": [{"id": l.id, "order": l.order_number} for l in lesson.module.lessons]}), 200


@api.route('/lessons', methods=['POST'])
@jwt_required()
def create_lesson():
    body = request.json
    lesson = Lesson(
        title=body["title"],
        content=body["content"],
        module_id=body["module_id"],
        order_number=body["order_number"]
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({"id": lesson.id, "title": lesson.title}), 201

# ---- QUIZZES ----


@api.route('/quizzes/<int:lesson_id>', methods=['GET'])
def get_quiz(lesson_id):
    quiz = db.session.execute(
        db.select(Quiz).filter_by(lesson_id=lesson_id)).scalar()
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify({"id": quiz.id, "questions": quiz.questions_data}), 200


@api.route('/quizzes', methods=['POST'])
@jwt_required()
def create_quiz():
    body = request.json
    quiz = Quiz(lesson_id=body["lesson_id"],
                questions_data=body["questions_data"])
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"id": quiz.id}), 201

# ---- USER PROGRESS ----


@api.route('/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_progress(user_id):

    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    progress = db.session.execute(
        db.select(UserProgress).filter_by(user_id=user_id)).scalars().all()

    if not progress:
        return jsonify([]), 200

    return jsonify([{"lesson_id": p.lesson_id, "lesson_title": p.lesson.title, "path_id": p.lesson.module.learning_path_id, "is_completed": p.is_completed, "quiz_score": p.quiz_score} for p in progress]), 200


@api.route('/progress/<int:user_id>/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson_progress(user_id, lesson_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "No tienes permiso para acceder a este recurso"}), 403

    progress = db.session.execute(db.select(UserProgress).filter_by(
        user_id=user_id, lesson_id=lesson_id)).scalars().one_or_none()

    if not progress:
        return jsonify({"lesson_id": lesson_id, "is_completed": False, "quiz_score": None}), 200

    return jsonify({"lesson_id": progress.lesson_id,
                    "is_completed": progress.is_completed,
                    "quiz_score": progress.quiz_score}), 200


@api.route('/progress', methods=['POST'])
@jwt_required()
def create_initial_progress():
    current_user_id = int(get_jwt_identity())
    body = request.get_json()

    if not isinstance(body, list):
        return jsonify({"error": "Se esperaba una lista de objetos JSON"}), 400

    if any(item.get("user_id") != current_user_id for item in body):
        return jsonify({"error": "No tienes permiso para crear progreso de otro usuario"}), 403

    initial_progress = []

    try:
        for item in body:
            progress = UserProgress(
                user_id=item["user_id"],
                lesson_id=item["lesson_id"],
                quiz_score=item.get("quiz_score", 0),
                is_completed=item.get("is_completed", False)
            )
            initial_progress.append(progress)

        db.session.add_all(initial_progress)
        db.session.commit()
        return jsonify({"message": "Progress created"}), 201

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500


@api.route('/progress/<int:user_id>/<int:lesson_id>', methods=['PUT'])
@jwt_required()
def update_progress(user_id, lesson_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "No tienes permiso para modificar este recurso"}), 403

    body = request.get_json(silent=True) or {}
    progress = db.session.execute(db.select(UserProgress).filter_by(
        user_id=user_id, lesson_id=lesson_id)).scalars().one_or_none()

    try:
        if not progress:
            progress = UserProgress(user_id=user_id, lesson_id=lesson_id)
            db.session.add(progress)

        progress.is_completed = body.get("is_completed", progress.is_completed)
        progress.quiz_score = body.get("quiz_score", progress.quiz_score)
        # La fecha de finalización alimenta las rachas de la gamificación.
        # Solo se sella la primera vez que la lección queda completada.
        if progress.is_completed and progress.completed_at is None:
            progress.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Progress updated"})

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500


@api.route('/dashboard', methods=['GET'])
@jwt_required()
def handle_dashboard():
    user_id = get_jwt_identity()
    user = db.get_or_404(User, int(user_id))
    return jsonify({"message": "Bienvenido", "user": user.serialize()}), 200


# ============================================================================
# GAMIFICACIÓN (XP, niveles, rachas) y CERTIFICADOS VERIFICABLES — Fase 2
# El XP y las rachas se DERIVAN del progreso ya guardado (sin tablas nuevas):
#   XP = 100 por lección completada + la nota de cada quiz registrado.
#   Racha = días consecutivos con al menos una lección completada
#   (usa UserProgress.completed_at; las filas antiguas sin fecha no cuentan).
# Los certificados sí se persisten (tabla certificates) para poder
# verificarlos públicamente por su código.
# ============================================================================

LEVELS = [
    (0, "Explorador"),
    (300, "Aprendiz de bloques"),
    (700, "Constructor"),
    (1200, "Validador"),
    (2000, "Nodo completo"),
    (3200, "Arquitecto Web3"),
]


def _calcular_xp(progress_rows):
    xp = 0
    for p in progress_rows:
        if p.is_completed:
            xp += 100
        if p.quiz_score is not None:
            xp += p.quiz_score
    return xp


def _nivel_desde_xp(xp):
    actual = LEVELS[0]
    siguiente = None
    for i, nivel in enumerate(LEVELS):
        if xp >= nivel[0]:
            actual = nivel
            siguiente = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return actual, siguiente


def _calcular_rachas(fechas):
    """Devuelve (racha actual, mejor racha, días activos) desde completed_at."""
    dias = sorted({f.date() for f in fechas if f is not None})
    if not dias:
        return 0, 0, 0
    mejor = 1
    racha = 1
    for i in range(1, len(dias)):
        racha = racha + 1 if (dias[i] - dias[i - 1]).days == 1 else 1
        mejor = max(mejor, racha)
    hoy = datetime.utcnow().date()
    actual = 0
    if dias[-1] in (hoy, hoy - timedelta(days=1)):
        actual = 1
        j = len(dias) - 1
        while j > 0 and (dias[j] - dias[j - 1]).days == 1:
            actual += 1
            j -= 1
    return actual, mejor, len(dias)


@api.route('/gamification/me', methods=['GET'])
@jwt_required()
def gamification_me():
    user_id = int(get_jwt_identity())
    rows = db.session.execute(
        db.select(UserProgress).filter_by(user_id=user_id)).scalars().all()

    xp = _calcular_xp(rows)
    (minimo, nombre), siguiente = _nivel_desde_xp(xp)
    actual, mejor, dias_activos = _calcular_rachas(
        [p.completed_at for p in rows])

    if siguiente:
        progreso_nivel = round((xp - minimo) / (siguiente[0] - minimo), 2)
        faltan = siguiente[0] - xp
    else:
        progreso_nivel = 1.0
        faltan = 0

    return jsonify({
        "xp": xp,
        "level_name": nombre,
        "level_min_xp": minimo,
        "next_level_name": siguiente[1] if siguiente else None,
        "next_level_xp": siguiente[0] if siguiente else None,
        "xp_to_next": faltan,
        "progress_to_next": progreso_nivel,
        "streak_current": actual,
        "streak_best": mejor,
        "active_days": dias_activos,
        "lessons_completed": sum(1 for p in rows if p.is_completed),
        "quizzes_passed": sum(
            1 for p in rows if p.quiz_score is not None and p.quiz_score >= 70),
    }), 200


def _resumen_ruta(user_id, path):
    """(total lecciones, completadas, títulos con quiz sin aprobar ≥70)."""
    lessons = [lesson for module in path.modules for lesson in module.lessons]
    ids = [lesson.id for lesson in lessons]
    rows = {}
    if ids:
        rows = {p.lesson_id: p for p in db.session.execute(
            db.select(UserProgress).filter_by(user_id=user_id)
            .where(UserProgress.lesson_id.in_(ids))).scalars().all()}
    completadas = sum(
        1 for lid in ids if rows.get(lid) and rows[lid].is_completed)
    pendientes_quiz = []
    for lesson in lessons:
        if lesson.quiz is not None:
            row = rows.get(lesson.id)
            if not row or row.quiz_score is None or row.quiz_score < 70:
                pendientes_quiz.append(lesson.title)
    return len(lessons), completadas, pendientes_quiz


@api.route('/certificates/claim', methods=['POST'])
@jwt_required()
def claim_certificate():
    user = db.session.get(User, int(get_jwt_identity()))
    body = request.get_json(silent=True) or {}
    path = db.session.get(LearningPath, body.get("path_id"))
    if not path:
        return jsonify({"error": "Ruta no encontrada"}), 404

    total, completadas, pendientes_quiz = _resumen_ruta(user.id, path)
    if total == 0 or completadas < total:
        return jsonify({
            "error": "Aún no completas todas las lecciones de esta ruta",
            "lessons_total": total,
            "lessons_completed": completadas,
        }), 400
    if pendientes_quiz:
        return jsonify({
            "error": "Te falta aprobar estos quizzes con 70% o más",
            "quizzes_pending": pendientes_quiz,
        }), 400

    existing = db.session.execute(
        db.select(Certificate).filter_by(
            user_id=user.id, learning_path_id=path.id)).scalars().one_or_none()
    if existing:
        return jsonify(existing.serialize()), 200

    issued = datetime.utcnow()
    digest = hashlib.sha256(
        f"{user.id}:{path.id}:{user.email}:{issued.isoformat()}".encode()
    ).hexdigest()[:15].upper()
    cert = Certificate(
        user_id=user.id,
        learning_path_id=path.id,
        code=f"BK-{digest[0:5]}-{digest[5:10]}-{digest[10:15]}",
        issued_at=issued,
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify(cert.serialize()), 201


@api.route('/certificates/mine', methods=['GET'])
@jwt_required()
def my_certificates():
    user_id = int(get_jwt_identity())
    certs = db.session.execute(
        db.select(Certificate).filter_by(user_id=user_id)
        .order_by(Certificate.issued_at.desc())).scalars().all()
    return jsonify([c.serialize() for c in certs]), 200


@api.route('/certificates/verify/<string:code>', methods=['GET'])
def verify_certificate(code):
    cert = db.session.execute(
        db.select(Certificate).filter_by(
            code=code.strip().upper())).scalars().one_or_none()
    if not cert:
        return jsonify({"valid": False}), 404
    return jsonify({
        "valid": True,
        "code": cert.code,
        "holder": cert.user.username or cert.user.email,
        "path": cert.learning_path.title,
        "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
    }), 200