import { useParams, Link } from "react-router-dom";
import CourseDescription from "../components/CourseDescription";
import ModuleCard from "../components/ModuleCard";
import { useEffect, useState } from "react";
import { getMyCertificates, claimCertificate } from "../services/gamificationService";
import useGlobalReducer from "../hooks/useGlobalReducer";
import { Award } from "lucide-react";

const CoursePage = () => {

    const [learningPath, setLearningPath] = useState();
    const [loadError, setLoadError] = useState("");
    const [userProgress, setUserProgress] = useState();
    const [cert, setCert] = useState(null);
    const [certError, setCertError] = useState("");
    const [claiming, setClaiming] = useState(false);
    const { store } = useGlobalReducer();
    const params = useParams();

    const verifyUser = () => {
        const user = localStorage.getItem("user");
        if (user) return JSON.parse(user).role;
        return null;
    }

    const getLearningPath = async () => {
        setLoadError("");
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/learning-paths/${params.theId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error("No es posible acceder a la información");
            }
            const data = await response.json();
            setLearningPath(data);

        } catch (error) {
            console.log(error);
            // Antes, un fallo de red dejaba el spinner girando para
            // siempre: ahora se muestra el error con forma de reintentar.
            setLoadError("No se pudo cargar esta ruta. Revisa tu conexión e inténtalo de nuevo.");
        }
    }

    const getUserProgress = async () => {
        if (verifyUser() === "student") {
            try {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/progress/${JSON.parse(localStorage.getItem("user")).id}`, {
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
                setUserProgress(data);

            } catch (error) {
                console.log(error);
            }
        }
    }

    const totalLessonsOfPath = () => {
        return learningPath?.modules.reduce((num, module) => num + module.lessons.length, 0);
    }

    const lessonsDoneOfPath = () => {
        return userProgress?.filter(progress => progress.is_completed === true).length;
    }

    const progressPath = () => {
        const total = totalLessonsOfPath();
        if (!total) return 0;
        return Math.round(lessonsDoneOfPath() * 100 / total);
    }

    useEffect(() => {
        getLearningPath();
        getUserProgress();
        if (verifyUser() === "student") {
            getMyCertificates(store.token)
                .then((certs) =>
                    setCert(certs.find((c) => c.path_id === parseInt(params.theId)) || null))
                .catch(() => {});
        }
    }, [params.theId])

    const handleClaim = async () => {
        setClaiming(true);
        setCertError("");
        try {
            const data = await claimCertificate(learningPath.id, store.token);
            setCert(data);
        } catch (err) {
            const pendientes = err.detail?.quizzes_pending;
            setCertError(
                pendientes?.length
                    ? `${err.message}: ${pendientes.join(", ")}`
                    : err.message
            );
        } finally {
            setClaiming(false);
        }
    };

    if (loadError) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger" role="alert">{loadError}</div>
                <div className="d-flex flex-wrap gap-2">
                    <button type="button" className="btn btn-primary rounded-pill px-4" onClick={getLearningPath}>
                        Reintentar
                    </button>
                    <Link to="/courses" className="btn btn-outline-primary rounded-pill px-4">
                        Ver todas las rutas
                    </Link>
                </div>
            </div>
        );
    }

    if (!learningPath) {
        return (
            <div className="container py-5 text-center" style={{ height: "75vh" }}>
                <div className="spinner-border" role="status">
                    <span className="visually-hidden">Cargando la ruta...</span>
                </div>
            </div>
        );
    }

    return <div className="container mt-4">
        <CourseDescription data={learningPath} userType={verifyUser()} />
        <div className="row my-3">
            <div className="col-12 col-lg-8">
                <div className="d-flex justify-content-between align-items-center mb-2">
                    <h3 className="fw-bold mb-0">Módulos</h3>
                    <span className="badge bg-primary-subtle text-primary-emphasis">
                        {learningPath?.number_of_modules} {learningPath?.number_of_modules === 1 ? "módulo" : "módulos"}
                    </span>
                </div>
                <div className="row">
                    {learningPath?.modules.sort((a, b) => a.id - b.id).map((module, index) => {
                        return <div key={module.id} className="col-12 col-md-6 mb-4">
                            <ModuleCard path={learningPath.id} data={module} order={index + 1} userType={verifyUser()} userProgress={userProgress} />
                        </div>
                    })}
                </div>
            </div>
            {verifyUser() === "student" ? <div className="col-12 col-lg-4 mt-4 mt-lg-0">
                <div className="card border-0 shadow-sm">
                    <div className="card-body p-4">
                        <span className="badge bg-primary-subtle text-primary-emphasis mb-2">
                            Tu avance
                        </span>
                        <h4 className="fw-bold mb-1">Estado de tu aprendizaje</h4>
                        <p className="text-muted small mb-3">
                            {progressPath()}% completado ({lessonsDoneOfPath()}/{totalLessonsOfPath()} lecciones)
                        </p>
                        <div className="progress" role="progressbar" aria-label="Progreso de la ruta"
                            aria-valuenow={progressPath()} aria-valuemin={0} aria-valuemax={100} style={{ height: "10px" }}>
                            <div className="progress-bar bg-primary"
                                style={{ width: `${progressPath()}%` }}></div>
                        </div>
                        {progressPath() === 100 && (
                            <div className="mt-3">
                                {cert ? (
                                    <Link to={`/certificado/${learningPath.id}`} className="btn btn-success rounded-pill px-4 d-inline-flex align-items-center gap-2">
                                        <Award size={16} /> Ver mi certificado
                                    </Link>
                                ) : (
                                    <>
                                        <button type="button" className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2"
                                            onClick={handleClaim} disabled={claiming}>
                                            <Award size={16} /> {claiming ? "Emitiendo..." : "Reclamar certificado"}
                                        </button>
                                        {certError && <p className="text-danger small mt-2 mb-0" role="alert">{certError}</p>}
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div> : ""}
        </div>
    </div>
}

export default CoursePage;