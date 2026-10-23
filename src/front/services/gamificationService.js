// Cliente de la API de gamificación (XP, niveles, rachas) y certificados.

const API = import.meta.env.VITE_BACKEND_URL;

// El token llega como parámetro desde el store global (useGlobalReducer),
// igual que el resto de la app construye sus cabeceras de autorización.
const authHeaders = (token) => ({
    "Content-Type": "application/json",
    Authorization: "Bearer " + token,
});

export const getGamification = async (token) => {
    const resp = await fetch(`${API}/api/gamification/me`, {
        headers: authHeaders(token),
    });
    if (!resp.ok) throw new Error("No se pudo cargar tu gamificación");
    return resp.json();
};

export const getMyCertificates = async (token) => {
    const resp = await fetch(`${API}/api/certificates/mine`, {
        headers: authHeaders(token),
    });
    if (!resp.ok) throw new Error("No se pudieron cargar tus certificados");
    return resp.json();
};

export const claimCertificate = async (pathId, token) => {
    const resp = await fetch(`${API}/api/certificates/claim`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ path_id: pathId }),
    });
    const data = await resp.json();
    if (!resp.ok) {
        const err = new Error(data.error || "No se pudo emitir el certificado");
        err.detail = data;
        throw err;
    }
    return data;
};

// Verificación pública: no requiere sesión.
export const verifyCertificate = async (code) => {
    const resp = await fetch(
        `${API}/api/certificates/verify/${encodeURIComponent(code)}`
    );
    if (resp.status === 404) return { valid: false };
    if (!resp.ok) throw new Error("No se pudo verificar el certificado");
    return resp.json();
};
