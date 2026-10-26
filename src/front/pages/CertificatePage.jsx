import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getMyCertificates } from "../services/gamificationService";
import useGlobalReducer from "../hooks/useGlobalReducer";
import { Logo } from "../components/Logo";
import { Printer, ArrowLeft, ShieldCheck } from "lucide-react";

// Muestra el certificado emitido para una ruta, listo para imprimir/guardar.
export const CertificatePage = () => {
    const { pathId } = useParams();
    const { store } = useGlobalReducer();
    const [cert, setCert] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getMyCertificates(store.token)
            .then((certs) =>
                setCert(certs.find((c) => c.path_id === parseInt(pathId)) || null)
            )
            .catch(() => setCert(null))
            .finally(() => setLoading(false));
    }, [pathId, store.token]);

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando el certificado...</span>
                </div>
            </div>
        );
    }

    if (!cert) {
        return (
            <div className="container py-5 text-center">
                <h3 className="fw-bold">Todavía no tienes este certificado</h3>
                <p className="text-secondary">
                    Completa el 100% de la ruta y aprueba sus quizzes con 70% o más
                    para poder emitirlo.
                </p>
                <Link to="/dashboard" className="btn btn-primary rounded-pill px-4">
                    Ir a mi panel
                </Link>
            </div>
        );
    }

    const fecha = cert.issued_at
        ? new Date(cert.issued_at).toLocaleDateString("es-ES", {
              day: "numeric",
              month: "long",
              year: "numeric",
          })
        : "";
    const verifyUrl = `${window.location.origin}/verificar/${cert.code}`;

    return (
        <div className="container py-5">
            <div className="d-flex flex-wrap gap-2 justify-content-between align-items-center mb-4 no-print">
                <Link
                    to="/dashboard"
                    className="btn btn-outline-secondary rounded-pill d-inline-flex align-items-center gap-2"
                >
                    <ArrowLeft size={16} /> Volver al panel
                </Link>
                <button
                    type="button"
                    className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2"
                    onClick={() => window.print()}
                >
                    <Printer size={16} /> Imprimir / guardar PDF
                </button>
            </div>

            <div className="bk-cert mx-auto">
                <div className="bk-cert-inner text-center">
                    <div className="d-flex justify-content-center mb-3">
                        <Logo size={44} />
                    </div>
                    <p className="bk-cert-eyebrow">Certificado de finalización</p>
                    <p className="text-muted mb-1">Blockali certifica que</p>
                    <h2 className="bk-cert-name">{cert.holder}</h2>
                    <p className="text-muted mb-1">ha completado satisfactoriamente la ruta</p>
                    <h3 className="bk-cert-path">{cert.path_title}</h3>
                    <p className="text-muted mb-4">
                        Superando todas las lecciones y evaluaciones con un mínimo del 70%.
                    </p>
                    <div className="d-flex justify-content-between align-items-end text-start flex-wrap gap-3">
                        <div>
                            <small className="text-muted d-block">Fecha de emisión</small>
                            <b>{fecha}</b>
                        </div>
                        <div className="text-end">
                            <small className="text-muted d-block">
                                <ShieldCheck size={13} className="me-1" />
                                Código de verificación
                            </small>
                            <b className="mono bk-break">{cert.code}</b>
                            <small className="text-muted d-block bk-break">
                                Verifícalo en {verifyUrl}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
