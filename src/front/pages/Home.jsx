import React from "react";
import { PriceTicker } from "../components/PriceTicker.jsx";
import { Hero } from "../components/Hero";
import { Features } from "../components/Features.jsx";
import { HowItWorks } from "../components/HowItWorks.jsx";
import LearningPaths from "../components/LearningPaths";
import { LabTeaser } from "../components/LabTeaser.jsx";
import { ForWho } from "../components/ForWho.jsx";
import { CTA } from "../components/CTA.jsx";

export const Home = () => {

	const verifyUser = () => {
		const user = localStorage.getItem("user");
		if (user) return JSON.parse(user).role;
		return null;
	}

	return (
		<>
			<PriceTicker />
			{/* Todas las secciones comparten un solo fondo continuo
			    (degradados + patrón de red blockchain + blobs suaves),
			    en vez de que cada sección tenga su propio fondo aislado. */}
			<div className="landing-decor">
				<div className="hero-blob" style={{ width: "320px", height: "320px", background: "#7c3aed", top: "-80px", left: "-100px" }}></div>
				<div className="hero-blob" style={{ width: "380px", height: "380px", background: "#06b6d4", top: "-60px", right: "-120px", animationDelay: "2s" }}></div>
				<div className="hero-blob" style={{ width: "300px", height: "300px", background: "#2563eb", top: "45%", left: "-140px", animationDelay: "3s" }}></div>
				<div className="hero-blob" style={{ width: "300px", height: "300px", background: "#7c3aed", top: "70%", right: "-120px", animationDelay: "5s" }}></div>
				<div className="hero-blob" style={{ width: "260px", height: "260px", background: "#06b6d4", bottom: "-100px", left: "30%", animationDelay: "4s" }}></div>

				<Hero />
				<Features />
				<HowItWorks />
				<LearningPaths />
				<LabTeaser />
				<ForWho />
			</div>
			{verifyUser() === null ? <CTA /> : ""}
		</>
	);
};
