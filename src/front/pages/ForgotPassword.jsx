import React, { useState } from "react";
import { Link } from "react-router-dom";

export const ForgotPassword = () => {
    const [email, setEmail] = useState("");
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/forgot-password`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "No se pudo procesar la solicitud.");
            }

            setSuccess(data.message || "Hemos enviado las instrucciones a tu correo electrónico.");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-5 d-flex justify-content-center">
            <div className="card border-0 shadow-sm" style={{ maxWidth: "420px", width: "100%" }}>
                <div className="card-body p-4 p-md-5">
                    <div className="text-center mb-4">
                        <span className="badge bg-primary-subtle text-primary-emphasis mb-3">
                            Recuperación de acceso
                        </span>
                        <h3 className="fw-bold mb-1">Recuperar Contraseña</h3>
                        <p className="text-muted small mb-0">
                            Ingresa tu correo y te enviaremos un enlace para restablecerla.
                        </p>
                    </div>

                    {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
                    {success && <div className="alert alert-success py-2" role="alert">{success}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label className="form-label fw-semibold" htmlFor="forgot-email">Correo Electrónico</label>
                            <input
                                id="forgot-email"
                                type="email"
                                autoComplete="email"
                                className="form-control"
                                placeholder="ejemplo@correo.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className="btn btn-primary w-100 rounded-pill py-2 fw-semibold"
                            disabled={loading}
                        >
                            {loading ? "Enviando..." : "Enviar Enlace de Recuperación"}
                        </button>
                    </form>

                    <p className="text-center text-muted small mt-4 mb-0">
                        <Link to="/login" className="text-primary fw-semibold">
                            ← Volver al Inicio de Sesión
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};