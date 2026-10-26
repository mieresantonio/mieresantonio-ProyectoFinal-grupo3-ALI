import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { getCourses } from "../services/coursesService";
import { CourseFilterBar } from "../components/CourseFilterBar";
import { CourseCard } from "../components/CourseCard";
import { User, FileText, CheckCircle2, ShieldCheck } from "lucide-react";

export const Courses = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchParams] = useSearchParams();
    const [searchText, setSearchText] = useState(searchParams.get("q") || "");
    const [activeLevel, setActiveLevel] = useState("Todas las Rutas");

    // Carga los cursos reales desde el backend al montar la página.
    // Es una función aparte para que el botón "Reintentar" pueda
    // volver a pedir los datos sin recargar toda la página.
    const cargar = () => {
        setLoading(true);
        setError(null);
        getCourses()
            .then((data) => setCourses(data))
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        cargar();
    }, []);

    // Filtra en el navegador (client-side) por texto y por nivel.
    const filteredCourses = courses.filter((course) => {
        const matchesSearch = course.title
            .toLowerCase()
            .includes(searchText.toLowerCase());
        const matchesLevel =
            activeLevel === "Todas las Rutas" || course.level === activeLevel;
        return matchesSearch && matchesLevel;
    });

    return (
        <div className="container py-4">
            {/* Encabezado + caja "Modo Explorador" */}
            <div className="row align-items-center mb-4">
                <div className="col-md-8">
                    <span className="badge bg-primary-subtle text-primary-emphasis mb-2">
                        CATÁLOGO EDUCATIVO WEB3
                    </span>
                    <h1 className="fw-bold">Explorar Rutas de Aprendizaje</h1>
                    <p className="text-muted">
                        El paso a paso desde conceptos fundamentales
                        de criptografía y consenso distribuido hasta el desarrollo de
                        contratos inteligentes y protocolos DeFi.
                    </p>
                </div>
                {localStorage.getItem("token") ? "" : <div className="col-md-4">
                    <div className="card border-0 shadow-sm p-3">
                        <h6 className="fw-bold d-flex align-items-center">
                            <User size={17} className="me-2 text-primary" />
                            Modo Explorador
                        </h6>
                        <p className="text-muted small">
                            Puedes consultar los temarios pero tienes que iniciar sesión para acceder a las
                            lecciones y guardar tu progreso.
                        </p>
                        <Link to="/register" className="btn btn-primary w-100 rounded-pill">Registrarme Gratis</Link>
                    </div>
                </div>}

            </div>

            {/* Buscador y filtros por nivel */}
            <CourseFilterBar
                searchText={searchText}
                onSearchChange={setSearchText}
                activeLevel={activeLevel}
                onLevelChange={setActiveLevel}
            />

            {loading && (
                <div className="text-center py-4">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Cargando rutas de aprendizaje...</span>
                    </div>
                    <p className="text-muted small mt-2 mb-0">Cargando rutas de aprendizaje...</p>
                </div>
            )}
            {error && (
                <div className="alert alert-danger" role="alert">
                    <p className="mb-2">{error}</p>
                    <button type="button" className="btn btn-outline-danger btn-sm rounded-pill px-3" onClick={cargar}>
                        Reintentar
                    </button>
                </div>
            )}
            {!loading && !error && filteredCourses.length === 0 && (
                <div className="py-3">
                    {courses.length === 0 ? (
                        <p className="text-muted">No hay rutas de aprendizaje todavía.</p>
                    ) : (
                        <>
                            <p className="text-muted mb-2">
                                Ninguna ruta coincide con tu búsqueda o filtro.
                            </p>
                            <button
                                type="button"
                                className="btn btn-outline-primary btn-sm rounded-pill px-3"
                                onClick={() => { setSearchText(""); setActiveLevel("Todas las Rutas"); }}
                            >
                                Limpiar filtros
                            </button>
                        </>
                    )}
                </div>
            )}

            {/* Grilla de tarjetas de cursos */}
            <div className="row g-4 mb-5">
                {filteredCourses.sort((a, b) => a.id - b.id).map((course) => (
                    <div className="col-12 col-md-6 col-lg-4" key={course.id}>
                        <CourseCard course={course} />
                    </div>
                ))}
            </div>

            {/* Franja de características, al final de la página */}
            <div className="row g-4 text-center">
                <div className="col-md-4">
                    <span className="icon-chip mb-3"><FileText size={22} /></span>
                    <h6 className="fw-bold">Lecturas Markdown Estructuradas</h6>
                    <p className="text-muted small">
                        Contenido técnico detallado con fragmentos de código listos para
                        inspeccionar y replicar.
                    </p>
                </div>
                <div className="col-md-4">
                    <span className="icon-chip green mb-3"><CheckCircle2 size={22} /></span>
                    <h6 className="fw-bold">Evaluaciones Interactivas</h6>
                    <p className="text-muted small">
                        Quizzes al finalizar cada módulo para afianzar conceptos clave con
                        explicación didáctica.
                    </p>
                </div>
                <div className="col-md-4">
                    <span className="icon-chip cyan mb-3"><ShieldCheck size={22} /></span>
                    <h6 className="fw-bold">Acreditación Académica</h6>
                    <p className="text-muted small">
                        Certificados digitales emitidos al completar el 100% de los
                        módulos y evaluaciones.
                    </p>
                </div>
            </div>
        </div>
    );
};