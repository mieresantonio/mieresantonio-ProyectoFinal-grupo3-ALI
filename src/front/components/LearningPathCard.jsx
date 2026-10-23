import { Link } from "react-router-dom";
import { BookOpen, Clock } from "lucide-react";

const LEVEL_BADGE_CLASS = {
    Principiante: "bg-info-subtle text-info-emphasis",
    Intermedio: "bg-warning-subtle text-warning-emphasis",
    Avanzado: "bg-danger-subtle text-danger-emphasis",
};

const LearningPathCard = ({ data }) => {
    const badgeClass = LEVEL_BADGE_CLASS[data.level] || "bg-secondary-subtle";

    return <div className="card h-100 bk-hover overflow-hidden">
        {data.image_url ? (
            <img className="card-img-top" src={data.image_url} alt={data.title}
                style={{ height: "160px", objectFit: "cover" }} />
        ) : (
            <div className="bk-path-banner" aria-hidden="true"></div>
        )}
        <div className="card-body d-flex flex-column">
            <div className="mb-2">
                <span className={`badge ${badgeClass}`}>{data.level}</span>
            </div>
            <h5 className="card-title fw-bold">{data.title}</h5>
            <p className="card-text text-secondary flex-grow-1">{data.description}</p>
            <div className="d-flex justify-content-between align-items-center mt-2">
                <small className="text-secondary d-inline-flex align-items-center gap-1">
                    <BookOpen size={14} />
                    {data.number_of_modules} {data.number_of_modules === 1 ? "Módulo" : "Módulos"}
                </small>
                <small className="text-secondary d-inline-flex align-items-center gap-1">
                    <Clock size={14} />{data.time_required}
                </small>
            </div>
            <Link to={`/course/${data.id}`} className="btn btn-primary btn-sm rounded-pill mt-3">
                Ver Temario
            </Link>
        </div>
    </div>
}

export default LearningPathCard;
