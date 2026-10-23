import React from "react";
import { Wallet, Code, GraduationCap } from "lucide-react";

export const ForWho = () => {
    const perfiles = [
        {
            Icon: Wallet,
            chip: "",
            titulo: "Ya usas crypto, pero no sabes qué hay debajo",
            texto: "Compras, vendes, quizá hasta usas DeFi. Pero no tienes claro qué es un consenso ni por qué una clave privada importa tanto."
        },
        {
            Icon: Code,
            chip: "violet",
            titulo: "Programas y quieres entrar a Web3",
            texto: "Sabes JavaScript o Python y ves que Solidity aparece en todas partes. Necesitas los fundamentos antes de escribir tu primer contrato."
        },
        {
            Icon: GraduationCap,
            chip: "cyan",
            titulo: "Empiezas desde cero",
            texto: "Escuchaste de blockchain y quieres entenderlo de verdad, sin hype ni promesas de rendimientos."
        }
    ];

    return (
        <section className="py-5">
            <div className="container">
                <div className="text-center mb-5">
                    <span className="bk-eyebrow justify-content-center mb-2">Para quién</span>
                    <h2 className="fw-bold">¿Para quién es <span className="gradient-heading">esto</span>?</h2>
                    <p className="text-secondary">
                        No hace falta saber programar para empezar.
                    </p>
                </div>
                <div className="row g-4">
                    {perfiles.map((perfil, i) => (
                        <div className="col-12 col-md-4" key={i}>
                            <div className="card bk-hover h-100 p-4">
                                <span className={`icon-chip ${perfil.chip} mb-3`}>
                                    <perfil.Icon size={22} />
                                </span>
                                <h6 className="fw-bold mb-2">{perfil.titulo}</h6>
                                <p className="text-secondary small mb-0">{perfil.texto}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
