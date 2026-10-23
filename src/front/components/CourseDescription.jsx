import { Link } from "react-router-dom";
import { Clock, BookOpen, Play, ArrowLeft } from "lucide-react";

const CourseDescription = ({ data, userType }) => {

    const totalLessons = data?.modules.reduce((num, module) =>
        num + module.lessons.length, 0);

    return <div className="container bg-dark text-white rounded-4 p-4 p-md-5">
        <div className="row align-items-center">
            <div className="col-md-6 d-flex flex-column justify-content-between">
                <div className="d-flex flex-wrap gap-2 mb-3">
                    <span className="badge bg-success-subtle text-success-emphasis rounded-pill px-3 py-2">
                        {data?.level}
                    </span>
                    <span className="badge bg-primary-subtle rounded-pill px-3 py-2 d-inline-flex align-items-center gap-1">
                        <Clock size={13} /> {data?.time_required}
                    </span>
                    <span className="badge bg-primary-subtle rounded-pill px-3 py-2 d-inline-flex align-items-center gap-1">
                        <BookOpen size={13} /> {totalLessons} {totalLessons === 1 ? "Lección" : "Lecciones"}
                    </span>
                </div>
                <div>
                    <h3 className="fw-bold display-6">{data?.title}</h3>
                    <p className="text-white-50">{data?.description}</p>
                </div>
                <div className="d-flex flex-wrap gap-2 mt-2">
                    {userType === "student" ? (
                        <Link to={`/lesson/${data?.id}/${data?.modules[0].lessons[0].id}`} className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2">
                            <Play size={16} /> Comenzar ahora
                        </Link>
                    ) : ""}
                    <Link to="/courses" className="btn btn-outline-light rounded-pill px-4 d-inline-flex align-items-center gap-2">
                        <ArrowLeft size={16} /> Ver todas las rutas
                    </Link>
                </div>
            </div>
            <div className="col-md-6 align-content-center mt-4 mt-md-0">
                {data?.image_url ? (
                    <img className="img-fluid rounded-3 shadow" src={data?.image_url} alt={data?.title} />
                ) : (
                    <div className="bk-path-banner rounded-3" style={{ height: "240px" }} aria-hidden="true"></div>
                )}
            </div>
        </div>
    </div>
}

export default CourseDescription;