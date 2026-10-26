import React, { useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";

export const ResetPassword = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const navigate = useNavigate();

    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        if (!token) {
            setError("No se proporcionó ningún token de recuperación.");
            return;
        }
        if (password.length < 6) {
            setError("La contraseña debe tener al menos 6 caracteres.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Las contraseñas no coinciden.");
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/reset-password`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token, password }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "No se pudo restablecer la contraseña.");
            }

            setSuccess(data.message || "Tu contraseña ha sido restablecida con éxito. Ya puedes iniciar sesión.");
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
                            Último paso
                        </span>
                        <h3 className="fw-bold mb-1">Restablecer Contraseña</h3>
                        <p className="text-muted small mb-0">
                            Ingresa tu nueva contraseña para acceder a tu cuenta.
                        </p>
                    </div>

                    {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
                    {success && <div className="alert alert-success py-2" role="alert">{success}</div>}

                    {success ? (
                        <button
                            className="btn btn-primary w-100 rounded-pill py-2 fw-semibold"
                            onClick={() => navigate("/login")}
                        >
                            Ir al Inicio de Sesión →
                        </button>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label className="form-label fw-semibold" htmlFor="reset-password">Nueva Contraseña</label>
                                <input
                                    id="reset-password"
                                    type="password"
                                    autoComplete="new-password"
                                    className="form-control"
                                    placeholder="Mínimo 6 caracteres"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="mb-4">
                                <label className="form-label fw-semibold" htmlFor="reset-password-confirm">Confirmar Nueva Contraseña</label>
                                <input
                                    id="reset-password-confirm"
                                    type="password"
                                    autoComplete="new-password"
                                    className="form-control"
                                    placeholder="Repite la nueva contraseña"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className="btn btn-primary w-100 rounded-pill py-2 fw-semibold"
                                disabled={loading}
                            >
                                {loading ? "Guardando..." : "Guardar Contraseña"}
                            </button>
                        </form>
                    )}

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