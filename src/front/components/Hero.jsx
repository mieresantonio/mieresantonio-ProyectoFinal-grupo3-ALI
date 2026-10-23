import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export const Hero = () => {

    const verifyUser = () => {
        const user = localStorage.getItem("user");
        if (user) return JSON.parse(user).role;
        return null;
    }

    return (
        <div className="container">
            <div className="text-center py-5">
                <span className="bk-hero-badge mb-4" data-aos="fade-down">
                    <span className="dot"></span>
                    Nueva ruta disponible: Desarrollo de Smart Contracts
                </span>

                <h1 className="mb-3 display-4 fw-bold" data-aos="fade-up">
                    Domina el futuro con <span className="gradient-heading">Blockchain</span>,<br />
                    aprendiendo haciendo
                </h1>

                <p className="lead text-secondary mb-4 mx-auto" style={{ maxWidth: "640px" }} data-aos="fade-up" data-aos-delay="100">
                    Rutas de aprendizaje guiadas desde cero hasta construir en Web3.
                    Sin videos interminables: lectura profunda, laboratorio interactivo
                    y evaluaciones reales con tu progreso guardado.
                </p>

                <div data-aos="fade-up" data-aos-delay="200">
                    {verifyUser() === null ?
                        <Link to="/register" className="btn btn-primary btn-lg me-2">
                            Empieza a aprender gratis <ArrowRight size={18} className="ms-1" />
                        </Link> : ""}
                    <Link to="/courses" className="btn btn-outline-primary btn-lg">
                        Ver plan de estudios
                    </Link>
                </div>

                <p className="small text-secondary mt-3 mb-0" data-aos="fade-up" data-aos-delay="250">
                    Sin tarjeta · Tu progreso se guarda en tu cuenta · Certificado al completar cada ruta
                </p>

                <div className="bk-stats row g-0 mt-5 mx-auto" style={{ maxWidth: "760px" }} data-aos="fade-up" data-aos-delay="300">
                    <div className="col-6 col-md-3 py-3 px-2">
                        <b>2</b>
                        <span>rutas completas</span>
                    </div>
                    <div className="col-6 col-md-3 py-3 px-2">
                        <b>70%</b>
                        <span>nota para aprobar</span>
                    </div>
                    <div className="col-6 col-md-3 py-3 px-2">
                        <b>100%</b>
                        <span>en español y práctico</span>
                    </div>
                    <div className="col-6 col-md-3 py-3 px-2">
                        <b>24/7</b>
                        <span>a tu ritmo, sin horarios</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
