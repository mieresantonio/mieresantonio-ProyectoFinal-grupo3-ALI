import React from "react";

export const HowItWorks = () => {
    const pasos = [
        {
            numero: "01",
            titulo: "Elige tu ruta",
            texto: "Empieza por los fundamentos o salta directo a smart contracts si ya tienes base."
        },
        {
            numero: "02",
            titulo: "Aprende haciendo",
            texto: "Lecciones escritas con ejemplos reales y un laboratorio para experimentar con hashes y bloques sin riesgo."
        },
        {
            numero: "03",
            titulo: "Demuestra que lo entendiste",
            texto: "Cada lección cierra con una evaluación. Necesitas 70% para avanzar, y tu progreso queda guardado."
        }
    ];

    return (
        <section className="py-5">
            <div className="container">
                <div className="text-center mb-5">
                    <span className="bk-eyebrow justify-content-center mb-2">Cómo funciona</span>
                    <h2 className="fw-bold">Tres pasos y estás <span className="gradient-heading">construyendo criterio</span></h2>
                </div>
                <div className="row g-4">
                    {pasos.map((paso) => (
                        <div className="col-12 col-md-4" key={paso.numero}>
                            <div className="card bk-hover h-100 p-4">
                                <div className="step-num mb-3">{paso.numero}</div>
                                <h5 className="fw-bold mb-2">{paso.titulo}</h5>
                                <p className="text-secondary mb-0">{paso.texto}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
