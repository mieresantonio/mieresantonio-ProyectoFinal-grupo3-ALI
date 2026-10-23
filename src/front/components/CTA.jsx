import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export const CTA = () => {
    return (
        <section className="py-5">
            <div className="container">
                <div
                    className="text-center text-white py-5 px-4"
                    style={{
                        borderRadius: "26px",
                        border: "1px solid rgba(148,163,184,.26)",
                        background: "radial-gradient(560px 260px at 50% -10%, rgba(124,58,237,.30), transparent 65%), linear-gradient(180deg, #0d1730, #0a1226)"
                    }}
                >
                    <h2 className="fw-bold mb-3">Tu primer bloque se crea <span className="gradient-heading">hoy</span></h2>
                    <p className="text-white-50 mb-4 mx-auto" style={{ maxWidth: "520px" }}>
                        Crea tu cuenta gratis y arranca con la primera ruta: tu primera lección
                        con quiz la terminas en menos de 15 minutos. Sin tarjeta, sin suscripción.
                    </p>
                    <Link to="/register" className="btn btn-primary btn-lg rounded-pill px-4">
                        Crear cuenta gratis <ArrowRight size={18} className="ms-1" />
                    </Link>
                </div>
            </div>
        </section>
    );
};
