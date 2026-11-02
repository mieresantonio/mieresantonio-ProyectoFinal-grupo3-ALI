import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { GraduationCap, Send, BookOpen, Sparkles } from "lucide-react";
import { askTutor } from "../services/tutorService";

// Tutor de Blockali: responde SOLO con fragmentos de las propias
// lecciones de la plataforma (búsqueda local en el backend, sin IA
// externa). Si el tema no está en las lecciones, lo dice y sugiere
// la lección más cercana.

const SUGERENCIAS = [
    "¿Qué es una blockchain?",
    "¿Qué pasa si pierdo mi frase semilla?",
    "¿Cómo funciona el slashing en Proof of Stake?",
    "¿Para qué sirve require en Solidity?",
];

const MENSAJE_INICIAL = {
    role: "tutor",
    text:
        "Hola, soy el tutor de Blockali. Pregúntame sobre lo que enseñan " +
        "las lecciones de la plataforma y te respondo con ese contenido, " +
        "citando la lección de origen. Si algo no está en las lecciones, " +
        "te lo digo en vez de inventarlo.",
    sources: [],
};

export const Tutor = () => {
    const [messages, setMessages] = useState([MENSAJE_INICIAL]);
    const [input, setInput] = useState("");
    const [sending, setSending] = useState(false);
    const [error, setError] = useState("");
    const endRef = useRef(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, sending]);

    const send = async (text) => {
        const question = (text ?? input).trim();
        if (!question || sending) return;
        setError("");
        setInput("");
        setMessages((prev) => [...prev, { role: "user", text: question }]);
        setSending(true);
        try {
            const data = await askTutor(question);
            setMessages((prev) => [
                ...prev,
                { role: "tutor", text: data.answer, sources: data.sources || [] },
            ]);
        } catch (e) {
            setError("No se pudo contactar al tutor. Revisa tu conexión e inténtalo de nuevo.");
        } finally {
            setSending(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        send();
    };

    return (
        <div className="container py-5" style={{ maxWidth: "820px" }}>
            <div className="text-center mb-4">
                <p className="bk-eyebrow justify-content-center mb-2">
                    <Sparkles size={16} className="me-1" /> Tutor de la plataforma
                </p>
                <h1 className="fw-bold d-flex align-items-center justify-content-center gap-2">
                    <GraduationCap size={34} /> Pregúntale a las lecciones
                </h1>
                <p className="text-secondary mx-auto" style={{ maxWidth: "620px" }}>
                    Este tutor responde <strong>solo desde las lecciones de Blockali</strong>:
                    busca en su contenido y te cita la lección de origen. No usa
                    servicios externos ni inventa respuestas fuera del temario.
                </p>
            </div>

            <div
                className="card border-0 shadow-sm mb-3"
                style={{ maxHeight: "55vh", overflowY: "auto" }}
            >
                <div className="card-body d-flex flex-column gap-3">
                    {messages.map((msg, i) => (
                        <div
                            key={i}
                            className={
                                msg.role === "user"
                                    ? "align-self-end text-end"
                                    : "align-self-start"
                            }
                            style={{ maxWidth: "88%" }}
                        >
                            <div
                                className={
                                    msg.role === "user"
                                        ? "badge text-wrap text-start bg-primary text-white p-3 rounded-4"
                                        : "badge text-wrap text-start bg-body-secondary text-body p-3 rounded-4"
                                }
                                style={{ fontSize: "0.95rem", fontWeight: 400, lineHeight: 1.55 }}
                            >
                                {msg.text}
                            </div>
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-2 text-start">
                                    <span className="small text-secondary d-block mb-1">
                                        <BookOpen size={13} className="me-1" />
                                        Fuentes en las lecciones:
                                    </span>
                                    {msg.sources.map((s, j) => (
                                        <Link
                                            key={j}
                                            to={`/lesson/${s.path_id}/${s.lesson_id}`}
                                            className="d-block small"
                                        >
                                            «{s.lesson_title}» — {s.path_title} · {s.module_title}
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                    {sending && (
                        <p className="text-secondary small mb-0">
                            Buscando en las lecciones…
                        </p>
                    )}
                    <div ref={endRef} />
                </div>
            </div>

            {error && (
                <div className="alert alert-danger py-2" role="alert">
                    {error}
                </div>
            )}

            <div className="d-flex flex-wrap gap-2 mb-3">
                {SUGERENCIAS.map((s) => (
                    <button
                        key={s}
                        type="button"
                        className="btn btn-outline-primary btn-sm rounded-pill"
                        onClick={() => send(s)}
                        disabled={sending}
                    >
                        {s}
                    </button>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="d-flex gap-2">
                <label htmlFor="tutor-input" className="visually-hidden">
                    Tu pregunta sobre las lecciones
                </label>
                <input
                    id="tutor-input"
                    type="text"
                    className="form-control rounded-pill"
                    placeholder="Ej.: ¿qué es la mempool?"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    maxLength={500}
                    disabled={sending}
                />
                <button
                    type="submit"
                    className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2"
                    disabled={sending || !input.trim()}
                >
                    <Send size={16} /> Preguntar
                </button>
            </form>
        </div>
    );
};
