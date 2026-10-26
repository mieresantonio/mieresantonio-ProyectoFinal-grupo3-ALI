import { Link } from "react-router-dom";

// Página de error 404: ruta desconocida o enlace roto.
export const NotFound = () => {
    return (
        <div className="container py-5 text-center">
            <p className="bk-eyebrow justify-content-center mb-2">Página no encontrada</p>
            <h1 className="fw-bold mb-3">Esta ruta no existe en Blockali</h1>
            <p className="text-secondary mx-auto mb-4" style={{ maxWidth: "520px" }}>
                Es posible que el enlace esté incompleto o que la página haya cambiado.
                Puedes volver al inicio o explorar las rutas de aprendizaje.
            </p>
            <div className="d-flex flex-wrap justify-content-center gap-2">
                <Link to="/" className="btn btn-primary rounded-pill px-4">
                    Volver al inicio
                </Link>
                <Link to="/courses" className="btn btn-outline-primary rounded-pill px-4">
                    Ver las rutas
                </Link>
            </div>
        </div>
    );
};
