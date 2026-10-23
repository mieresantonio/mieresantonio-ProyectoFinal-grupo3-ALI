import React from "react";
import { Link } from "react-router-dom";
import { Hash, Blocks, ArrowRight } from "lucide-react";

// Sección de la landing que presenta el Laboratorio interactivo.
export const LabTeaser = () => {
    return (
        <section className="py-5">
            <div className="container">
                <div className="lab-panel">
                    <div className="row align-items-center g-4">
                        <div className="col-12 col-lg-6">
                            <span className="bk-eyebrow mb-2">Laboratorio</span>
                            <h3 className="fw-bold mb-3">La blockchain se entiende <span className="gradient-heading">tocándola</span></h3>
                            <p className="text-secondary mb-4">
                                Nada de quedarse en la teoría: calcula la huella digital (hash) de cualquier
                                texto en vivo y altera un bloque para ver, con tus propios ojos, cómo la
                                cadena detecta la falsificación. Sin dinero real, sin riesgo.
                            </p>
                            <Link to="/laboratorio" className="btn btn-primary rounded-pill px-4">
                                Entrar al laboratorio <ArrowRight size={17} className="ms-1" />
                            </Link>
                        </div>
                        <div className="col-12 col-lg-6">
                            <div className="d-flex flex-column gap-3">
                                <div className="d-flex gap-3 align-items-start">
                                    <span className="icon-chip cyan"><Hash size={20} /></span>
                                    <div>
                                        <h6 className="fw-bold mb-1">Huella digital SHA-256</h6>
                                        <p className="text-secondary small mb-0">
                                            Escribe algo y observa su hash calculado al instante, igual que
                                            lo hace la red con cada bloque.
                                        </p>
                                    </div>
                                </div>
                                <div className="d-flex gap-3 align-items-start">
                                    <span className="icon-chip violet"><Blocks size={20} /></span>
                                    <div>
                                        <h6 className="fw-bold mb-1">Altera la cadena</h6>
                                        <p className="text-secondary small mb-0">
                                            Falsifica el dato de un bloque y comprueba por qué su hash deja
                                            de coincidir: así se defiende una blockchain.
                                        </p>
                                    </div>
                                </div>
                                <div className="lab-hash-out mono">
                                    sha256("Blockali") = 8f2b1c…a904 — pruébalo tú mismo →
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
