import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { verifyCertificate } from "../services/gamificationService";
import { ShieldCheck, ShieldX } from "lucide-react";

// Página pública: cualquiera con el código puede comprobar que un
// certificado de Blockali es auténtico.
export const VerifyPage = () => {
    const { code } = useParams();
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        verifyCertificate(code)
            .then(setResult)
            .catch(() => setResult({ valid: false }))
            .finally(() => setLoading(false));
    }, [code]);

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Verificando el certificado…</span>
                </div>
                <p className="text-secondary small mt-3">Verificando el certificado…</p>
            </div>
        );
    }

    return (
        <div className="container py-5" style={{ maxWidth: "640px" }}>
            <div className="card bk-hover p-4 p-md-5 text-center">
                {result?.valid ? (
                    <>
                        <span className="icon-chip green mx-auto mb-3">
                            <ShieldCheck size={24} />
                        </span>
                        <h3 className="fw-bold mb-2">Certificado válido</h3>
                        <p className="text-secondary mb-4">
                            Blockali confirma la autenticidad de este certificado.
                        </p>
                        <div className="text-start mx-auto" style={{ maxWidth: "420px" }}>
                            <p className="mb-2">
                                <small className="text-secondary d-block">Titular</small>
                                <b>{result.holder}</b>
                            </p>
                            <p className="mb-2">
                                <small className="text-secondary d-block">Ruta completada</small>
                                <b>{result.path}</b>
                            </p>
                            <p className="mb-2">
                                <small className="text-secondary d-block">Fecha de emisión</small>
                                <b>
                                    {result.issued_at
                                        ? new Date(result.issued_at).toLocaleDateString("es-ES", {
                                              day: "numeric",
                                              month: "long",
                                              year: "numeric",
                                          })
                                        : "—"}
                                </b>
                            </p>
                            <p className="mb-0">
                                <small className="text-secondary d-block">Código</small>
                                <b className="mono bk-break">{result.code}</b>
                            </p>
                        </div>
                    </>
                ) : (
                    <>
                        <span className="icon-chip mx-auto mb-3" style={{ background: "rgba(248,113,113,.13)", color: "#f87171" }}>
                            <ShieldX size={24} />
                        </span>
                        <h3 className="fw-bold mb-2">Certificado no encontrado</h3>
                        <p className="text-secondary mb-4">
                            El código <b className="mono">{code}</b> no corresponde a ningún
                            certificado emitido por Blockali. Revisa que esté escrito completo,
                            con sus guiones.
                        </p>
                        <Link to="/" className="btn btn-primary rounded-pill px-4">
                            Conocer Blockali
                        </Link>
                    </>
                )}
            </div>
        </div>
    );
};
