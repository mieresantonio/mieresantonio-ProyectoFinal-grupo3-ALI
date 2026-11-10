import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CheckCircle2, Circle, ArrowLeft, ArrowRight } from "lucide-react";

const LessonPage = () => {

    const params = useParams();
    const [lesson, setLesson] = useState();
    const [loadError, setLoadError] = useState("");
    const [userProgress, setUserProgress] = useState({});
    const [error, setError] = useState("");
    // Guarda de carrera por recurso (P1, ronda 14): mismo diseño que en
    // CoursePage — cada llamada toma el siguiente número de su secuencia
    // y solo escribe si sigue siendo la más reciente de ese recurso.
    const lessonSeq = useRef(0);
    const progressSeq = useRef(0);

    // Lee el usuario de forma segura: si no hay sesión, devuelve null
    // en vez de tronar con JSON.parse(null).role
    const getCurrentUser = () => {
        const raw = localStorage.getItem("user");
        return raw ? JSON.parse(raw) : null;
    };
    const currentUser = getCurrentUser();

    const getLesson = async () => {
        const seq = ++lessonSeq.current;
        setLoadError("");
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/lessons/${params.lessonId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error("No se pudo obtener información");
            }

            const data = await response.json();
            if (seq !== lessonSeq.current) return;
            setLesson(data);

        } catch (error) {
            if (seq !== lessonSeq.current) return;
            // Antes, un fallo de red dejaba el spinner girando para
            // siempre: ahora se muestra el error con forma de reintentar.
            setLoadError("No se pudo cargar esta lección. Revisa tu conexión e inténtalo de nuevo.");
        }
    };

    const getUserProgress = async () => {
        if (currentUser?.role === "student") {
            const seq = ++progressSeq.current;
            try {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress/${currentUser.id}/${params.lessonId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    }
                });

                if (!response.ok) {
                    throw new Error("No se pudo obtener el progreso del usuario");
                }

                const data = await response.json();
                if (seq !== progressSeq.current) return;
                setUserProgress(data);

            } catch (error) {
            }
        }
    };

    const handleLessonDone = async () => {

        if (!currentUser) return;
        setError("");

        if (!userProgress.is_completed) {
            try {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress/${currentUser.id}/${params.lessonId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${localStorage.getItem("token")}`
                    },
                    body: JSON.stringify({
                        "is_completed": true
                    })
                });

                if (!response.ok) {
                    throw new Error("No se pudo guardar el progreso");
                }

                const data = await response.json();
                setUserProgress({ ...userProgress, is_completed: true });

            } catch (error) {
                setError(error.message);
            }
        }
    };

    const previousLessonId = () => {
        const lessons = lesson.module_lessons || [];
        const current = lessons.find(lesson => lesson.id === parseInt(params.lessonId));
        if (!current) return "";
        // Antes se buscaba exactamente order - 1: con órdenes no contiguos
        // dentro del módulo (p. ej. 1 y 3) no había coincidencia, se
        // devolvía "" y «Anterior» construía /lesson/<pathId>/, que cae
        // en el 404. Ahora se toma la lección existente de mayor orden
        // menor que el de la actual (la anterior real, haya hueco o no);
        // si no hay ninguna, se devuelve "" y la página muestra
        // «Volver al Curso» en vez de «Anterior».
        const previousLessons = lessons.filter(lesson => lesson.order < current.order);
        if (previousLessons.length === 0) return "";
        const previousLesson = previousLessons.reduce((a, b) => (b.order > a.order ? b : a));
        return previousLesson.id;
    };


    const nextLessonId = () => {
        const lessons = lesson.module_lessons || [];
        const current = lessons.find(lesson => lesson.id === parseInt(params.lessonId));
        if (!current) return "quiz";
        // Antes se buscaba exactamente order + 1: con órdenes no contiguos
        // dentro del módulo (p. ej. 1 y 3) no había coincidencia, se
        // devolvía "quiz" y «Siguiente» saltaba al quiz saltándose la
        // lección existente de orden 3. Ahora se toma la lección existente
        // de menor orden mayor que el de la actual (la siguiente real,
        // haya hueco o no), simétrico a previousLessonId; solo si no hay
        // ninguna siguiente se devuelve "quiz".
        const nextLessons = lessons.filter(lesson => lesson.order > current.order);
        if (nextLessons.length === 0) return "quiz";
        const nextLesson = nextLessons.reduce((a, b) => (b.order < a.order ? b : a));
        return nextLesson.id;
    };

    useEffect(() => {
        getLesson();
        getUserProgress();
    }, [params.lessonId]);

    if (loadError) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger" role="alert">{loadError}</div>
                <div className="d-flex flex-wrap gap-2">
                    <button type="button" className="btn btn-primary rounded-pill px-4" onClick={getLesson}>
                        Reintentar
                    </button>
                    <Link to={`/course/${params.pathId}`} className="btn btn-outline-primary rounded-pill px-4">
                        Volver al curso
                    </Link>
                </div>
            </div>
        );
    }

    if (!lesson) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando la lección...</span>
                </div>
            </div>
        );
    }

    const hasQuiz = (lesson.module_lessons || []).length > 0;

    return <div className="container mt-4">
        {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
        <div className="d-flex flex-wrap gap-2 align-items-center">
            <div>
                <span className="badge bg-primary-subtle text-primary-emphasis rounded-pill px-3 py-2">
                    Lección {lesson?.order_number}
                </span>
            </div>
            {currentUser?.role === "student" ?
                <div className="ms-auto">
                    <button type="button"
                        className={`btn ${userProgress?.is_completed ?
                            "btn-success" : "btn-outline-success"} rounded-pill d-inline-flex align-items-center gap-2`}
                        onClick={handleLessonDone}>
                        {userProgress?.is_completed ?
                            <CheckCircle2 size={17} /> : <Circle size={17} />} {userProgress?.is_completed ?
                                "Completado" : "Marcar como completado"}
                    </button>
                </div> : ""}
        </div>
        <div className="card border-0 shadow-sm mt-3">
            <div className="card-body p-4 p-md-5">
                {lesson?.content?.trim() ? (
                    <div className="lesson-content">
                        <Markdown remarkPlugins={[remarkGfm]}>{lesson?.content}</Markdown>
                    </div>
                ) : (
                    <p className="text-muted mb-0">
                        Esta lección aún no tiene contenido. Vuelve pronto: el equipo
                        la está preparando.
                    </p>
                )}
            </div>
        </div>
        <div className="d-flex flex-wrap gap-2 justify-content-between pt-4 pb-2">
            {previousLessonId() === "" ? <Link to={`/course/${params.pathId}`} className="btn btn-outline-secondary rounded-pill d-inline-flex align-items-center gap-2">
                <ArrowLeft size={16} /> Volver al Curso
            </Link> : <Link to={`/lesson/${params.pathId}/${previousLessonId()}`} className="btn btn-outline-secondary rounded-pill d-inline-flex align-items-center gap-2">
                <ArrowLeft size={16} /> Anterior
            </Link>}
            {nextLessonId() !== "quiz" ?
                <Link to={`/lesson/${params.pathId}/${nextLessonId()}`} className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2">
                    Siguiente <ArrowRight size={16} />
                </Link>
                : hasQuiz ? <Link to={`/quizzes/${params.lessonId}`} className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2">
                    Ir al Quiz <ArrowRight size={16} />
                </Link> : <Link to={`/course/${params.pathId}`} className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2">
                    Volver al Curso <ArrowRight size={16} />
                </Link>}
        </div>
    </div>;

};

export default LessonPage;