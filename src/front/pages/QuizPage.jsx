import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getQuizByLesson } from "../services/quizService.js";

export const QuizPage = () => {
    const { lessonId } = useParams();
    const [quiz, setQuiz] = useState(null);
    const [quizError, setQuizError] = useState("");
    const [respuestas, setRespuestas] = useState({});
    const [enviado, setEnviado] = useState(false);
    const [error, setError] = useState("");
    const params = useParams();

    // Lee el usuario de forma segura: si no hay sesión, devuelve null
    // en vez de tronar con JSON.parse(null).role
    const getCurrentUser = () => {
        const raw = localStorage.getItem("user");
        return raw ? JSON.parse(raw) : null;
    };
    const currentUser = getCurrentUser();

    const setScore = async () => {
        if (!currentUser) return;
        setError("");

        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress/${currentUser.id}/${params.lessonId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    "quiz_score": calcularNota() / quiz.questions_data.length * 100,
                })
            });

            if (!response.ok) {
                throw new Error("No se pudo guardar el score");
            }

            const data = await response.json();

            setEnviado(true);

        } catch (error) {
            setError(error.message);
        }
    }

    const cargarQuiz = () => {
        setQuizError("");
        // Antes, un fallo de red dejaba el spinner girando para
        // siempre: ahora se muestra el error con forma de reintentar.
        getQuizByLesson(lessonId)
            .then((data) => setQuiz(data))
            .catch(() => setQuizError("No se pudo cargar el quiz. Revisa tu conexión e inténtalo de nuevo."));
    };

    useEffect(() => {
        cargarQuiz();
    }, [lessonId]);

    const calcularNota = () => {
        let correctas = 0;
        quiz.questions_data.forEach((pregunta, index) => {
            if (respuestas[index] === pregunta.correct_option) {
                correctas++;
            }
        });
        return correctas;
    };

    if (quizError) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger" role="alert">{quizError}</div>
                <div className="d-flex flex-wrap gap-2">
                    <button type="button" className="btn btn-primary rounded-pill px-4" onClick={cargarQuiz}>
                        Reintentar
                    </button>
                    <Link to="/courses" className="btn btn-outline-primary rounded-pill px-4">
                        Ver las rutas
                    </Link>
                </div>
            </div>
        );
    }

    if (!quiz) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando el quiz...</span>
                </div>
            </div>
        );
    }

    if (!quiz.questions_data || quiz.questions_data.length === 0) {
        return (
            <div className="container py-5 text-center">
                <h3 className="fw-bold">Este quiz aún no tiene preguntas</h3>
                <p className="text-secondary">
                    El equipo está preparando las preguntas de esta evaluación.
                    Vuelve pronto.
                </p>
                <Link to="/courses" className="btn btn-primary rounded-pill px-4">
                    Ver las rutas
                </Link>
            </div>
        );
    }

    return (
        <div className="container py-4">
            {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
            <div className="card border-0 shadow-sm mb-4">
                <div className="card-body p-4">
                    <span className="badge bg-primary-subtle text-primary-emphasis rounded-pill px-3 py-2 mb-2">
                        EVALUACIÓN
                    </span>
                    <h3 className="fw-bold">{quiz.title}</h3>
                    {currentUser?.role === "student" ?
                        <p className="text-muted mb-0">{quiz.description}</p> : ""}
                </div>
            </div>
            {quiz.questions_data.map((pregunta, index) => (
                <div className="card border-0 shadow-sm mb-3" key={index}>
                    <div className="card-body p-4">
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <span className="badge bg-primary-subtle rounded-pill px-3 py-2">
                                Pregunta {index + 1} de {quiz.questions_data.length}
                            </span>
                            {currentUser?.role === "student" ?
                                <span className="small text-muted">Selecciona una respuesta</span> : ""}
                        </div>
                        <h5 className="fw-bold mb-3">{pregunta.question_text}</h5>

                        {["a", "b", "c"].map((letra) => (
                            <button
                                type="button"
                                key={letra}
                                disabled={enviado}
                                aria-pressed={respuestas[index] === letra}
                                className={`quiz-option mb-2
                                        ${respuestas[index] === letra ? "border-primary bg-primary-subtle" : ""}
                                        ${letra === pregunta.correct_option &&
                                        currentUser?.role === "admin" ?
                                        "bg-success-subtle border-success" : ""}`}
                                onClick={() => { if (!enviado) setRespuestas({ ...respuestas, [index]: letra }) }}
                            >
                                <span className="badge bg-primary-subtle me-2">
                                    {letra.toUpperCase()}
                                </span>
                                {pregunta["option_" + letra]}
                            </button>
                        )
                        )}
                    </div>
                </div>
            ))}
            {currentUser?.role !== "student" ? "" : !enviado ? (
                <button
                    className="btn btn-primary rounded-pill px-4"
                    onClick={() => setScore()}
                    disabled={Object.keys(respuestas).length < quiz.questions_data.length}
                >
                    Enviar respuestas
                </button>
            ) : (
                <div className="card border-0 shadow-sm">
                    <div className="card-body text-center p-4">
                        <h4 className="fw-bold">
                            {calcularNota()} de {quiz.questions_data.length} correctas
                        </h4>
                        <p className="text-muted mb-0">
                            {calcularNota() / quiz.questions_data.length >= 0.7
                                ? "Aprobaste la evaluación."
                                : "Necesitas 70% para aprobar. Puedes intentarlo de nuevo."}
                        </p>
                        <button
                            className="btn btn-outline-primary rounded-pill px-4 mt-3"
                            onClick={() => {
                                setRespuestas({});
                                setEnviado(false);
                            }}
                        >
                            Intentar de nuevo
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};