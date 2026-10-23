import React from "react";
import { FileText, ClipboardCheck, Network, FlaskConical } from "lucide-react";

export const Features = () => {
    const features = [
        {
            Icon: FileText,
            chip: "",
            title: "Enfoque en texto",
            text: "Lee a tu propio ritmo. El material escrito permite escaneo rápido, búsqueda de conceptos y una absorción de conocimientos más eficiente que el video."
        },
        {
            Icon: ClipboardCheck,
            chip: "violet",
            title: "Evaluación continua",
            text: "Quizzes técnicos al final de cada lección para asegurar la comprensión de conceptos complejos como criptografía y consenso. Se aprueba con 70%."
        },
        {
            Icon: Network,
            chip: "cyan",
            title: "Rutas estructuradas",
            text: "No pierdas tiempo decidiendo qué aprender. Sigue un currículo lógico y progresivo, desde los fundamentos hasta tu primer contrato inteligente."
        },
        {
            Icon: FlaskConical,
            chip: "gold",
            title: "Laboratorio interactivo",
            text: "Calcula hashes en vivo, altera bloques y mira cómo la cadena se rompe. Los conceptos se entienden tocándolos, sin arriesgar dinero real."
        }
    ];

    return (
        <section className="py-5">
            <div className="container">
                <div className="text-center mb-5" data-aos="fade-up">
                    <span className="bk-eyebrow justify-content-center mb-2">Por qué Blockali</span>
                    <h2 className="fw-bold">¿Por qué elegir <span className="gradient-heading">Blockali</span>?</h2>
                    <p className="text-secondary mx-auto" style={{ maxWidth: "600px" }}>
                        Un enfoque pedagógico diseñado para desarrolladores y profesionales
                        que valoran su tiempo y buscan profundidad técnica.
                    </p>
                </div>

                <div className="row g-4">
                    {features.map((f, index) => (
                        <div className="col-12 col-md-6 col-lg-3" key={index} data-aos="fade-up" data-aos-delay={index * 100}>
                            <div className="card bk-hover h-100 p-4">
                                <span className={`icon-chip ${f.chip} mb-4`}>
                                    <f.Icon size={22} />
                                </span>
                                <h5 className="fw-bold mb-3">{f.title}</h5>
                                <p className="text-secondary mb-0">{f.text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
