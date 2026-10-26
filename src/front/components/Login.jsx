import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { dispatch } = useGlobalReducer();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await fetch(
                `${import.meta.env.VITE_BACKEND_URL}/api/login`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Correo o contraseña incorrectos");
            }

            dispatch({ type: "set_token", payload: data.token });
            dispatch({ type: "set_user", payload: data.user });
            localStorage.setItem("token", data.token);
            localStorage.setItem("user", JSON.stringify(data.user));

            navigate("/dashboard");
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
                            Bienvenido de nuevo
                        </span>
                        <h3 className="fw-bold mb-1">Iniciar Sesión</h3>
                        <p className="text-muted small mb-0">
                            Continúa tu ruta de aprendizaje en Blockali.
                        </p>
                    </div>

                    {error && <div className="alert alert-danger py-2" role="alert">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="mb-3">
                            <label className="form-label fw-semibold" htmlFor="login-email">Correo Electrónico</label>
                            <input
                                id="login-email"
                                type="email"
                                autoComplete="email"
                                className="form-control"
                                placeholder="estudiante@ejemplo.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="mb-4">
                            <div className="d-flex justify-content-between align-items-center">
                                <label className="form-label fw-semibold mb-0" htmlFor="login-password">Contraseña</label>
                                <Link to="/forgot-password" className="text-primary small">
                                    ¿Olvidaste tu contraseña?
                                </Link>
                            </div>
                            <input
                                id="login-password"
                                type="password"
                                autoComplete="current-password"
                                className="form-control mt-1"
                                placeholder="********"
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
                            {loading ? "Entrando..." : "Entrar"}
                        </button>
                    </form>

                    <p className="text-center text-muted small mt-4 mb-0">
                        ¿No tienes una cuenta?{" "}
                        <Link to="/register" className="text-primary fw-semibold">
                            Regístrate aquí
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};