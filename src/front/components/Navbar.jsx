import { Link, useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";
import { getCourses } from "../services/coursesService";
import { Logo } from "./Logo.jsx";

export const Navbar = () => {
	const { store, dispatch } = useGlobalReducer();
	const navigate = useNavigate();
	const [searchText, setSearchText] = useState("");
	const [suggestionsOpen, setSuggestionsOpen] = useState(false);
	const [courses, setCourses] = useState([]);

	// Carga la lista de cursos una sola vez, para poder sugerirlos
	// mientras el usuario escribe. Si falla, simplemente no hay
	// sugerencias de cursos.
	useEffect(() => {
		getCourses()
			.then((data) => setCourses(data))
			.catch(() => setCourses([]));
	}, []);

	const handleLogout = () => {
		dispatch({ type: "logout" });
		localStorage.removeItem("token");
		localStorage.removeItem("user");
		navigate("/");
	};

	const handleSearch = (e) => {
		e.preventDefault();
		navigate(`/courses?q=${encodeURIComponent(searchText)}`);
		setSuggestionsOpen(false);
	};

	const goTo = (path) => {
		navigate(path);
		setSearchText("");
		setSuggestionsOpen(false);
	};

	// Opciones fijas del buscador. "Mis Cursos" solo aparece con sesión
	// iniciada. "Admin" nunca se incluye aquí a propósito.
	const staticOptions = [{ label: "Rutas de Aprendizaje", path: "/courses" }];
	if (store.token) {
		staticOptions.push({ label: "Mis Cursos", path: "/dashboard" });
	}

	const query = searchText.toLowerCase();
	const matchingStatic = staticOptions.filter((o) =>
		o.label.toLowerCase().includes(query)
	);
	const matchingCourses = courses
		.filter((c) => c.title.toLowerCase().includes(query))
		.map((c) => ({ label: c.title, path: `/course/${c.id}` }));

	const suggestions = [...matchingStatic, ...matchingCourses];

	return (
		<nav className="navbar sticky-top py-3" aria-label="Navegación principal">
			<div className="container d-flex flex-wrap align-items-center justify-content-between">
				<Link to="/" aria-label="Blockali — inicio">
					<Logo size={32} />
				</Link>

				<form
					onSubmit={handleSearch}
					className="flex-grow-1 d-flex justify-content-center px-2 px-lg-4 position-relative"
				>
					<input
						type="text"
						className="form-control rounded-pill"
						style={{ maxWidth: "400px" }}
						placeholder="¿Qué quieres aprender hoy?"
						aria-label="Buscar rutas de aprendizaje"
						value={searchText}
						onChange={(e) => setSearchText(e.target.value)}
						onFocus={() => setSuggestionsOpen(true)}
						onBlur={() => setTimeout(() => setSuggestionsOpen(false), 150)}
					/>

					{suggestionsOpen && suggestions.length > 0 && (
						<ul
							className="list-group position-absolute shadow-sm"
							style={{ top: "100%", width: "min(400px, calc(100vw - 2rem))", zIndex: 1000 }}
						>
							{suggestions.map((item, i) => (
								<li key={i} className="list-group-item p-0">
									<button
										type="button"
										className="btn w-100 text-start"
										onMouseDown={() => goTo(item.path)}
									>
										{item.label}
									</button>
								</li>
							))}
						</ul>
					)}
				</form>

				{/* En pantallas grandes, los enlaces van junto al buscador. */}
				<div className="d-none d-lg-flex align-items-center gap-2">
					<Link to="/courses" className="btn btn-outline-primary rounded-pill">
						Explorar Rutas
					</Link>
					<Link to="/laboratorio" className="btn btn-outline-primary rounded-pill">
						Laboratorio
					</Link>

					{store.token ? (
						<>
							<Link to="/dashboard" className="btn btn-outline-primary rounded-pill">
								Mis Cursos
							</Link>
							<button type="button" className="btn btn-outline-danger rounded-pill" onClick={handleLogout}>
								Cerrar Sesión
							</button>
						</>
					) : (
						<>
							<Link to="/register" className="btn btn-outline-primary rounded-pill">
								Registrarse
							</Link>
							<Link to="/login" className="btn btn-primary rounded-pill">
								Iniciar Sesión
							</Link>
						</>
					)}
				</div>

				{/* En móvil y tablet, los mismos enlaces en una fila
				    desplazable debajo del buscador: sin ellos, la barra
				    desbordaba la pantalla. */}
				<div className="d-flex d-lg-none gap-2 w-100 mt-2 overflow-auto flex-nowrap">
					<Link to="/courses" className="btn btn-outline-primary btn-sm rounded-pill flex-shrink-0">
						Explorar Rutas
					</Link>
					<Link to="/laboratorio" className="btn btn-outline-primary btn-sm rounded-pill flex-shrink-0">
						Laboratorio
					</Link>

					{store.token ? (
						<>
							<Link to="/dashboard" className="btn btn-outline-primary btn-sm rounded-pill flex-shrink-0">
								Mis Cursos
							</Link>
							<button type="button" className="btn btn-outline-danger btn-sm rounded-pill flex-shrink-0" onClick={handleLogout}>
								Cerrar Sesión
							</button>
						</>
					) : (
						<>
							<Link to="/register" className="btn btn-outline-primary btn-sm rounded-pill flex-shrink-0">
								Registrarse
							</Link>
							<Link to="/login" className="btn btn-primary btn-sm rounded-pill flex-shrink-0">
								Iniciar Sesión
							</Link>
						</>
					)}
				</div>
			</div>
		</nav>
	);
};