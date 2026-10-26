import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export const Register = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/signup`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "No se pudo crear la cuenta");
            }

            setSuccess(
                data.message ||
                "Usuario registrado con éxito. Te hemos enviado un correo de verificación."
            );
            setUsername("");
            setEmail("");
            setPassword("");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-5 d-flex justify-content-center">
            <div className="card border-0 shadow-sm" style={{ maxWidth: "460px", width: "100%" }}>
                <div className="card-body p-4 p-md-5">
                    <div className="text-center mb-4">
                        <span className="badge bg-primary-subtle text-primary-emphasis mb-3">
                            Empieza gratis
                        </span>
                        <h3 className="fw-bold mb-1">Crear Cuenta</h3>
                        <p className="text-muted small mb-0">
                            Únete y arranca tu primera ruta de blockchain hoy.
                        </p>
                    </div>

                    {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}
                    {success && <div className="alert alert-success py-2" role="alert">{success}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="mb-3">
                            <label className="form-label fw-semibold" htmlFor="register-username">Nombre de Usuario</label>
                            <input
                                id="register-username"
                                type="text"
                                autoComplete="username"
                                className="form-control"
                                placeholder="Tu nombre"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>

                        <div className="mb-3">
                            <label className="form-label fw-semibold" htmlFor="register-email">Correo Electrónico</label>
                            <input
                                id="register-email"
                                type="email"
                                autoComplete="email"
                                className="form-control"
                                placeholder="ejemplo@correo.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label fw-semibold" htmlFor="register-password">Contraseña</label>
                            <input
                                id="register-password"
                                type="password"
                                autoComplete="new-password"
                                className="form-control"
                                placeholder="Mínimo 6 caracteres"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary w-100 rounded-pill py-2 fw-semibold"
                            disabled={loading}
                        >
                            {loading ? "Registrando..." : "Registrarse"}
                        </button>
                    </form>

                    <p className="text-center text-muted small mt-4 mb-0">
                        ¿Ya tienes una cuenta?{" "}
                        <Link to="/login" className="text-primary fw-semibold">
                            Inicia Sesión
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};