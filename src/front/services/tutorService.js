// Cliente del Tutor de Blockali (POST /api/tutor).
// El endpoint es público, igual que el contenido de las lecciones:
// no necesita sesión ni token.

const API = import.meta.env.VITE_BACKEND_URL;

export const askTutor = async (question) => {
    const resp = await fetch(`${API}/api/tutor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.error || "El tutor no pudo responder ahora");
    }
    return data;
};
