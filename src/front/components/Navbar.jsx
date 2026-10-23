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
		<nav className="navbar sticky-top py-3">
			<div className="container d-flex align-items-center justify-content-between">
				<Link to="/">
					<Logo size={32} />
				</Link>

				<form
					onSubmit={handleSearch}
					className="flex-grow-1 d-flex justify-content-center px-4 position-relative"
				>
					<input
						type="text"
						className="form-control rounded-pill"
						style={{ maxWidth: "400px" }}
						placeholder="¿Qué quieres aprender hoy?"
						value={searchText}
						onChange={(e) => setSearchText(e.target.value)}
						onFocus={() => setSuggestionsOpen(true)}
						onBlur={() => setTimeout(() => setSuggestionsOpen(false), 150)}
					/>

					{suggestionsOpen && suggestions.length > 0 && (
						<ul
							className="list-group position-absolute shadow-sm"
							style={{ top: "100%", width: "400px", zIndex: 1000 }}
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

				<div className="d-flex align-items-center gap-2">
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
							<button className="btn btn-outline-danger rounded-pill" onClick={handleLogout}>
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
			</div>
		</nav>
	);
};