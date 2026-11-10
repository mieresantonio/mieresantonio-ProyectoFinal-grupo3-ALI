import { Link } from "react-router-dom";
import PropTypes from "prop-types";
import { CheckCircle2, FileText, ArrowRight, GraduationCap, Play } from "lucide-react";

const ModuleCard = ({ path, data, order, userType, userProgress }) => {

    const verifyProgress = (lesson) => {
        const progress = userProgress?.find(progress => progress.lesson_id === lesson.id);
        if (!progress) return false;

        return progress.is_completed;
    };

    return <div className="card h-100 border-0 shadow-sm">
        <div className="card-header border-0 pt-3" style={{ background: "transparent" }}>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="badge bg-primary-subtle text-primary-emphasis rounded-pill px-3">
                    Módulo {order}
                </span>
                <span className="text-muted small">
                    {data?.lessons.length} {data?.lessons.length === 1 ? "lección" : "lecciones"}
                </span>
            </div>
            <h4 className="fw-bold mb-0">{data?.title}</h4>
        </div>
        <ul className="list-group list-group-flush h-100">
            {data?.lessons.sort((a, b) => a.id - b.id).map((lesson, index) => {
                return <li key={lesson.id} className="list-group-item container py-3">
                    <div className="row justify-content-between align-items-center">
                        <div className="col d-flex align-items-center">
                            {verifyProgress(lesson) ?
                                <CheckCircle2 size={22} className="text-success flex-shrink-0" />
                                : <FileText size={22} className="text-secondary flex-shrink-0" />}
                            <div className="d-flex flex-column justify-content-center ms-3">
                                <h6 className="m-0 text-break">{lesson.title}</h6>
                            </div>
                        </div>
                        {userType === "student" ?
                            <div className="col-auto">
                                {verifyProgress(lesson) ?
                                    <Link to={`/lesson/${path}/${lesson.id}`}
                                        className="btn btn-outline-success btn-sm py-1 rounded-pill d-inline-flex align-items-center gap-1">
                                        Repasar <ArrowRight size={13} />
                                    </Link>
                                    : <Link to={`/lesson/${path}/${lesson.id}`}
                                        className="btn btn-outline-primary btn-sm py-1 rounded-pill d-inline-flex align-items-center gap-1">
                                        Leer Lección <ArrowRight size={13} />
                                    </Link>}
                            </div>
                            : userType === "admin" ?
                                <div className="col-auto"><Link to={`/lesson/${path}/${lesson.id}`}
                                    className="btn btn-outline-secondary btn-sm py-1 rounded-pill">
                                    Ver Lección</Link></div> : ""}
                    </div>
                </li>;
            })}
        </ul>
        <div className="card-footer border-0 d-flex justify-content-between align-items-center py-3" style={{ background: "transparent" }}>
            <span className="text-secondary small d-inline-flex align-items-center gap-2">
                <GraduationCap size={16} /> Evaluación del módulo
            </span>
            <div>
                {data?.lessons?.length === 0 ?
                    <span className="text-muted small">Sin lecciones aún</span>
                    : userType === "student" ?
                        <Link to={`/quizzes/${data.lessons[data.lessons.length - 1].id}`} className="btn btn-primary btn-sm py-1 rounded-pill px-3 d-inline-flex align-items-center gap-1">
                            Realizar Quiz <Play size={12} />
                        </Link>
                        : userType === "admin" ?
                            <Link to={`/quizzes/${data.lessons[data.lessons.length - 1].id}`} className="btn btn-outline-secondary btn-sm py-1 rounded-pill px-3">
                                Ver Quiz
                            </Link> : ""}
            </div>
        </div>
    </div>;
};

// Formas según la API: `data` es un módulo de GET /api/learning-paths/<id>
// (routes.py: {id, title, lessons: [{id, title}]}; Module.title es
// nullable=False en models.py) y `userProgress` es la lista de
// GET /api/progress/<user_id> ({lesson_id, is_completed, ...}).
// `userType` es el rol de User.serialize(): "student" | "admin", o null
// sin sesión (verifyUser en CoursePage.jsx), por eso no es requerido;
// `userProgress` solo se carga para estudiantes y el componente ya lo
// lee con `?.`, tampoco requerido.
ModuleCard.propTypes = {
    path: PropTypes.number.isRequired,
    data: PropTypes.shape({
        title: PropTypes.string.isRequired,
        lessons: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.number.isRequired,
            title: PropTypes.string.isRequired
        })).isRequired
    }).isRequired,
    order: PropTypes.number.isRequired,
    userType: PropTypes.oneOf(["student", "admin"]),
    userProgress: PropTypes.arrayOf(PropTypes.shape({
        lesson_id: PropTypes.number.isRequired,
        is_completed: PropTypes.bool
    }))
};

export default ModuleCard;