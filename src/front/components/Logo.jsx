import PropTypes from "prop-types";

export const Logo = ({ size = 32, showText = true, color = "currentColor" }) => {
    return (
        <div className="d-inline-flex align-items-center gap-2">
            <svg
                width={size}
                height={size}
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Bloque superior izquierdo */}
                <rect x="4" y="6" width="16" height="16" rx="3" stroke={color} strokeWidth="3" />
                {/* Bloque inferior derecho */}
                <rect x="28" y="26" width="16" height="16" rx="3" stroke={color} strokeWidth="3" />
                {/* Bloque central, relleno */}
                <rect x="16" y="16" width="16" height="16" rx="3" fill={color} />
                {/* Eslabón que conecta el primero con el central */}
                <line x1="14" y1="20" x2="18" y2="20" stroke={color} strokeWidth="3" strokeLinecap="round" />
                {/* Eslabón que conecta el central con el último */}
                <line x1="30" y1="28" x2="34" y2="28" stroke={color} strokeWidth="3" strokeLinecap="round" />
            </svg>

            {showText && (
                <span className="fw-bold" style={{ fontSize: size * 0.6, letterSpacing: "-0.02em" }}>
                    Blockali
                </span>
            )}
        </div>
    );
};

// Las 3 props tienen valor por defecto en la firma, así que ninguna
// es requerida. Forma según el uso real: `size` se usa como width/
// height del SVG y en la aritmética size * 0.6 (número; los llamantes
// Navbar.jsx y CertificatePage.jsx pasan 32 y 44), `showText` decide
// un render condicional (bool) y `color` alimenta stroke/fill del SVG
// (cadena, p. ej. el "currentColor" por defecto).
Logo.propTypes = {
    size: PropTypes.number,
    showText: PropTypes.bool,
    color: PropTypes.string
};