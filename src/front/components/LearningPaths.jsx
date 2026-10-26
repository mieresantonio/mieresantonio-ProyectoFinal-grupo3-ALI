import { useEffect } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";
import LearningPathCard from "./LearningPathCard";
import { Link } from "react-router-dom";

const LearningPaths = () => {

    const { store, dispatch } = useGlobalReducer();

    const getLearningPaths = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/learning-paths`);
            const data = await response.json();
            dispatch({ type: "set_learning_paths", payload: data })
        } catch (error) {
            console.log(error);
        }
    }

    useEffect(() => {
        getLearningPaths();
    }, [])

    return <div className="container py-5">
        <div className="row text-center mb-4">
            <span className="bk-eyebrow justify-content-center mb-2">Catálogo educativo Web3</span>
            <h3 className="fw-bold">Rutas de <span className="gradient-heading">Aprendizaje</span></h3>
        </div>
        <div className="row g-4 pb-5">
            {store.learningPaths?.map((value, index) => {
                return <div key={value.id} className="col-12 col-md-6 col-lg-4">
                    <LearningPathCard data={value} />
                </div>
            })}
        </div>
        <div className="row">
            <div className="col-12 text-center pb-2">
                <Link to="/courses" className="btn btn-outline-primary rounded-pill px-4">
                    Ver todas las rutas
                </Link>
            </div>
        </div>
    </div>
}

export default LearningPaths;