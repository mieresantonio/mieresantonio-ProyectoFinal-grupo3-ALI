import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { CheckCircle2, XCircle, ArrowRight, RotateCcw } from "lucide-react";

export const VerifyEmail = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");

    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState({ success: false, message: "" });

    useEffect(() => {
        let activo = true;
        const verifyUserToken = async () => {
            if (!token) {
                setStatus({
                    success: false,
                    message: "No se proporcionó ningún token de verificación."
                });
                setLoading(false);
                return;
            }

            try {
                const backendUrl = import.meta.env.VITE_BACKEND_URL;
                const response = await fetch(`${backendUrl}/api/verify-email`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Error al verificar la cuenta.");
                }

                if (activo) setStatus({
                    success: true,
                    message: data.message || "¡Cuenta verificada exitosamente!"
                });
            } catch (error) {
                if (activo) setStatus({
                    success: false,
                    message: error.message || "El enlace es inválido o ha expirado."
                });
            } finally {
                if (activo) setLoading(false);
            }
        };

        verifyUserToken();
        return () => { activo = false; };
    }, [token]);

    return (
        <div className="container py-5 d-flex justify-content-center">
            <div className="card border-0 shadow-sm text-center" style={{ maxWidth: "420px", width: "100%" }}>
                <div className="card-body p-4 p-md-5">
                    {loading ? (
                        <div>
                            <div
                                className="spinner-border text-primary mb-3"
                                role="status"
                                style={{ width: "3rem", height: "3rem" }}
                            >
                                <span className="visually-hidden">Verificando ...</span>
                            </div>
                            <h4 className="fw-bold">Verificando tu cuenta ...</h4>
                            <p className="text-muted small mb-0">Por favor espera un momento.</p>
                        </div>
                    ) : (
                        <div>
                            <div className="d-flex justify-content-center mb-3">
                                {status.success ? (
                                    <CheckCircle2 size={64} className="text-success" />
                                ) : (
                                    <XCircle size={64} className="text-danger" />
                                )}
                            </div>

                            <span className="badge bg-primary-subtle text-primary-emphasis mb-2">
                                {status.success ? "Verificación completa" : "Algo salió mal"}
                            </span>

                            <h4 className="fw-bold mb-3">
                                {status.success ? "Verificación Exitosa" : "Verificación Fallida"}
                            </h4>

                            <p className="text-muted small mb-4">{status.message}</p>

                            {status.success ? (
                                <Link to="/login" className="btn btn-primary w-100 rounded-pill py-2 fw-semibold">
                                    Ir a Iniciar Sesión <ArrowRight size={18} className="ms-1" />
                                </Link>
                            ) : (
                                <Link to="/register" className="btn btn-outline-primary w-100 rounded-pill py-2 fw-semibold">
                                    <RotateCcw size={18} className="me-1" /> Volver a Registrarme
                                </Link>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};