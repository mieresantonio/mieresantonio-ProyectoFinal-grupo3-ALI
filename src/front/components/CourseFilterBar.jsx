import PropTypes from "prop-types";

const LEVELS = ["Todas las Rutas", "Principiante", "Intermedio", "Avanzado"];

export const CourseFilterBar = ({
    searchText,
    onSearchChange,
    activeLevel,
    onLevelChange
}) => {
    return (
        <div className="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
            <input
                type="text"
                className="form-control"
                style={{ maxWidth: "350px" }}
                placeholder="Buscar por título, Solidity, DeFi..."
                aria-label="Buscar rutas por título"
                value={searchText}
                onChange={(e) => onSearchChange(e.target.value)}
            />

            <div className="d-flex flex-wrap gap-2">
                {LEVELS.map((level) => (
                    <button
                        key={level}
                        type="button"
                        className={`btn btn-sm rounded-pill ${activeLevel === level ? "btn-primary" : "btn-outline-secondary"
                            }`}
                        onClick={() => onLevelChange(level)}
                    >
                        {level}
                    </button>
                ))}
            </div>
        </div>
    );
};

// Forma según el uso real en pages/Courses.jsx: el llamante mantiene
// `searchText` y `activeLevel` con useState (cadena siempre presente;
// el propio Courses filtra con searchText.toLowerCase() sin red) y
// pasa los setters de React como callbacks, invocados sin condición
// en onChange/onClick. `activeLevel` solo puede ser uno de los LEVELS
// de este fichero: el estado nace en "Todas las Rutas" y solo cambia
// desde los botones que renderiza este componente. Las 4 requeridas.
CourseFilterBar.propTypes = {
    searchText: PropTypes.string.isRequired,
    onSearchChange: PropTypes.func.isRequired,
    activeLevel: PropTypes.oneOf(LEVELS).isRequired,
    onLevelChange: PropTypes.func.isRequired
};