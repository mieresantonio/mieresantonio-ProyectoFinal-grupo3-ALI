import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Hash, Blocks, ShieldAlert, ShieldCheck, RotateCcw, ArrowRight } from "lucide-react";

// SHA-256 real, calculado en el navegador con Web Crypto.
const sha256 = async (text) => {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
};

const short = (h) => (h ? `${h.slice(0, 16)}…` : "—");

const DATOS_INICIALES = [
    "Ana envía 2 BTC a Bruno",
    "Bruno envía 0,5 BTC a Carla",
    "Carla envía 0,1 BTC a David",
];

export const Lab = () => {
    // --- Demo 1: hash en vivo ---
    const [texto, setTexto] = useState("Blockali");
    const [hashTexto, setHashTexto] = useState("");

    useEffect(() => {
        let activo = true;
        sha256(texto).then((h) => { if (activo) setHashTexto(h); });
        return () => { activo = false; };
    }, [texto]);

    // --- Demo 2: cadena falsificable ---
    const [datos, setDatos] = useState(DATOS_INICIALES);
    const [hashes, setHashes] = useState([]);
    const [rota, setRota] = useState(false);

    const recalcular = async (arr) => {
        const out = [];
        let prev = "0".repeat(64);
        for (const d of arr) {
            const h = await sha256(prev + "|" + d);
            out.push(h);
            prev = h;
        }
        setHashes(out);
    };

    useEffect(() => { recalcular(DATOS_INICIALES); }, []);

    // Editar un dato RECALCULA su hash y los de los bloques siguientes:
    // la cadena sigue siendo válida, pero ya no coincide con las copias
    // que guarda el resto de la red.
    const editarDato = (i, valor) => {
        const arr = [...datos];
        arr[i] = valor;
        setDatos(arr);
        setRota(false);
        recalcular(arr);
    };

    // Falsificar = cambiar el dato SIN recalcular el hash (a escondidas).
    // El hash registrado deja de corresponder al contenido y el bloque
    // siguiente apunta a un hash que ya no es el real: cadena rota.
    const falsificar = () => {
        const arr = [...datos];
        arr[1] = "Bruno envía 500 BTC a Eve";
        setDatos(arr);
        setRota(true);
    };

    const restaurar = () => {
        setDatos(DATOS_INICIALES);
        setRota(false);
        recalcular(DATOS_INICIALES);
    };

    return (
        <div className="container py-5">
            <div className="text-center mb-5">
                <span className="bk-eyebrow justify-content-center mb-2">Laboratorio interactivo</span>
                <h1 className="fw-bold">La blockchain se entiende <span className="gradient-heading">tocándola</span></h1>
                <p className="text-secondary mx-auto" style={{ maxWidth: "640px" }}>
                    Dos experimentos reales, calculados en tu navegador con el mismo algoritmo
                    SHA-256 que usa Bitcoin. Sin dinero, sin riesgo: solo conceptos hechos visibles.
                </p>
            </div>

            {/* ---------- Experimento 1: hash en vivo ---------- */}
            <div className="lab-panel mb-4">
                <div className="d-flex align-items-center gap-3 mb-3">
                    <span className="icon-chip cyan"><Hash size={22} /></span>
                    <div>
                        <h4 className="fw-bold mb-0">Experimento 1 · La huella digital (hash)</h4>
                        <small className="text-secondary">Escribe lo que sea y mira su SHA-256 cambiar al instante.</small>
                    </div>
                </div>
                <label className="form-label">Tu texto</label>
                <input
                    type="text"
                    className="form-control mb-3"
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder="Escribe cualquier cosa…"
                />
                <label className="form-label">Su hash SHA-256</label>
                <div className="lab-hash-out">{hashTexto}</div>
                <p className="text-secondary small mt-3 mb-0">
                    Prueba cambiar <b>una sola letra</b>: el hash cambia por completo (efecto avalancha).
                    Y no hay camino de vuelta: del hash no se puede recuperar el texto. Así se sellan los bloques.
                </p>
            </div>

            {/* ---------- Experimento 2: cadena falsificable ---------- */}
            <div className="lab-panel mb-4">
                <div className="d-flex align-items-center gap-3 mb-3">
                    <span className="icon-chip violet"><Blocks size={22} /></span>
                    <div>
                        <h4 className="fw-bold mb-0">Experimento 2 · Falsifica la cadena</h4>
                        <small className="text-secondary">Cada bloque guarda el hash del anterior. Por eso alterar el pasado se nota.</small>
                    </div>
                </div>

                <div className="row g-3 mb-3">
                    {datos.map((dato, i) => {
                        const prev = i === 0 ? "0".repeat(64) : hashes[i - 1];
                        const invalido = rota && i >= 1;
                        return (
                            <div className="col-12 col-md-4" key={i}>
                                <div className={`lab-block h-100 ${invalido ? "bad" : ""}`}>
                                    <div className="d-flex justify-content-between align-items-center mb-2">
                                        <b>Bloque {i + 1}</b>
                                        {invalido
                                            ? <span className="badge bg-danger-subtle text-danger-emphasis"><ShieldAlert size={12} className="me-1" />Inválido</span>
                                            : <span className="badge bg-success-subtle text-success-emphasis"><ShieldCheck size={12} className="me-1" />Válido</span>}
                                    </div>
                                    <label className="form-label small mb-1">Contenido</label>
                                    <input
                                        type="text"
                                        className="form-control form-control-sm mb-2"
                                        value={dato}
                                        onChange={(e) => editarDato(i, e.target.value)}
                                    />
                                    <div className="h">hash: {short(hashes[i])}</div>
                                    <div className="h">prev: {short(prev)}</div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {rota ? (
                    <div className="alert alert-danger d-flex align-items-start gap-2">
                        <ShieldAlert size={20} className="flex-shrink-0 mt-1" />
                        <span>
                            <b>Cadena rota y detectada.</b> El bloque 2 fue alterado a escondidas: su hash
                            registrado ya no corresponde a su contenido, y el bloque 3 apunta al hash
                            antiguo. Cualquier nodo de la red rechazaría esta versión. Para que el engaño
                            pasara, habría que recalcular este bloque <i>y todos los siguientes</i>… y
                            convencer a miles de copias a la vez.
                        </span>
                    </div>
                ) : (
                    <div className="alert alert-info d-flex align-items-start gap-2">
                        <ShieldCheck size={20} className="flex-shrink-0 mt-1" />
                        <span>
                            <b>Cadena íntegra.</b> Cada hash coincide con su contenido y cada bloque
                            apunta correctamente al anterior. Si editas un contenido a mano, los hashes
                            se recalculan — pero tu copia dejaría de coincidir con la del resto de la red.
                        </span>
                    </div>
                )}

                <div className="d-flex flex-wrap gap-2">
                    <button type="button" className="btn btn-primary rounded-pill px-4" onClick={falsificar}>
                        Falsificar el bloque 2
                    </button>
                    <button type="button" className="btn btn-outline-primary rounded-pill px-4 d-inline-flex align-items-center gap-2" onClick={restaurar}>
                        <RotateCcw size={15} /> Restaurar cadena
                    </button>
                </div>
            </div>

            <div className="text-center py-3">
                <p className="text-secondary mb-3">
                    Esto es solo el experimento 1 y 2. En las rutas aprendes el resto: wallets,
                    consenso, claves y tu primer contrato inteligente.
                </p>
                <Link to="/courses" className="btn btn-primary rounded-pill px-4 d-inline-flex align-items-center gap-2">
                    Ver las rutas de aprendizaje <ArrowRight size={16} />
                </Link>
            </div>
        </div>
    );
};
