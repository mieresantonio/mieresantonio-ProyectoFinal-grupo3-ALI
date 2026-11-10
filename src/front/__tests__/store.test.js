// Primeros tests de frontend de Blockali (Ronda 12, Bucle 1).
// Sin dependencias nuevas: runner integrado de Node (node --test) +
// node:assert. Ejecutar desde la raíz del repo:
//   node --test "src/front/__tests__/*.test.js"
// Fijan el comportamiento ACTUAL de src/front/store.js: si un test
// empieza a fallar, o cambió el reducer a propósito (actualizar aquí)
// o es una regresión.
import { describe, it, afterEach } from "node:test";
import assert from "node:assert/strict";
import storeReducer, { initialStore } from "../store.js";

// Estado base equivalente al que produce initialStore() sin sesión.
const makeStore = () => ({
  message: null,
  token: null,
  user: null,
  modules: [],
  learningPaths: []
});

describe("storeReducer", () => {
  it("set_learning_paths guarda las rutas y conserva el resto del estado", () => {
    const store = makeStore();
    const paths = [{ id: 1, title: "Blockchain desde cero" }];
    const next = storeReducer(store, { type: "set_learning_paths", payload: paths });
    assert.deepStrictEqual(next.learningPaths, paths);
    assert.strictEqual(next.token, null);
    assert.strictEqual(next.user, null);
    assert.deepStrictEqual(next.modules, []);
    assert.strictEqual(next.message, null);
  });

  it("set_learning_paths no muta el store original y devuelve un objeto nuevo", () => {
    const store = makeStore();
    const next = storeReducer(store, { type: "set_learning_paths", payload: [{ id: 2 }] });
    assert.notStrictEqual(next, store);
    assert.deepStrictEqual(store.learningPaths, []);
  });

  it("set_token guarda el token y conserva usuario y rutas", () => {
    const store = { ...makeStore(), user: { id: 7 }, learningPaths: [{ id: 1 }] };
    const next = storeReducer(store, { type: "set_token", payload: "tok-abc" });
    assert.strictEqual(next.token, "tok-abc");
    assert.deepStrictEqual(next.user, { id: 7 });
    assert.deepStrictEqual(next.learningPaths, [{ id: 1 }]);
    assert.strictEqual(store.token, null);
  });

  it("set_user guarda el usuario logueado", () => {
    const store = { ...makeStore(), token: "tok-abc" };
    const user = { id: 7, name: "Ana", email: "ana@example.com" };
    const next = storeReducer(store, { type: "set_user", payload: user });
    assert.deepStrictEqual(next.user, user);
    assert.strictEqual(next.token, "tok-abc");
  });

  it("set_user sobrescribe el usuario anterior (refresco del Dashboard)", () => {
    const store = { ...makeStore(), user: { id: 7, name: "Ana" } };
    const next = storeReducer(store, { type: "set_user", payload: { id: 7, name: "Ana M." } });
    assert.deepStrictEqual(next.user, { id: 7, name: "Ana M." });
  });

  it("logout limpia token y usuario pero conserva rutas y módulos", () => {
    const store = {
      message: null,
      token: "tok-abc",
      user: { id: 7 },
      modules: [{ id: 3 }],
      learningPaths: [{ id: 1 }]
    };
    const next = storeReducer(store, { type: "logout" });
    assert.strictEqual(next.token, null);
    assert.strictEqual(next.user, null);
    assert.deepStrictEqual(next.learningPaths, [{ id: 1 }]);
    assert.deepStrictEqual(next.modules, [{ id: 3 }]);
    assert.strictEqual(store.token, "tok-abc");
  });

  it("una acción desconocida devuelve el mismo store, sin cambios ni copia", () => {
    const store = makeStore();
    const next = storeReducer(store, { type: "accion_que_no_existe", payload: 123 });
    assert.strictEqual(next, store);
  });

  it("sin acción (argumento omitido) devuelve el mismo store", () => {
    const store = makeStore();
    assert.strictEqual(storeReducer(store), store);
  });

  it("una acción sin type devuelve el mismo store", () => {
    const store = makeStore();
    assert.strictEqual(storeReducer(store, {}), store);
    assert.strictEqual(storeReducer(store, { payload: "x" }), store);
  });
});

describe("initialStore", () => {
  // initialStore lee el global localStorage al llamarse (no al importar
  // el módulo), así que en Node basta simularlo antes de cada llamada.
  const installLocalStorage = (values) => {
    globalThis.localStorage = {
      getItem: (key) => (key in values ? values[key] : null)
    };
  };

  afterEach(() => {
    delete globalThis.localStorage;
  });

  it("sin sesión guardada devuelve el estado inicial vacío", () => {
    installLocalStorage({});
    assert.deepStrictEqual(initialStore(), {
      message: null,
      token: null,
      user: null,
      modules: [],
      learningPaths: []
    });
  });

  it("recupera token y usuario guardados en localStorage", () => {
    installLocalStorage({
      token: "tok-guardado",
      user: JSON.stringify({ id: 7, name: "Ana" })
    });
    const store = initialStore();
    assert.strictEqual(store.token, "tok-guardado");
    assert.deepStrictEqual(store.user, { id: 7, name: "Ana" });
    assert.deepStrictEqual(store.modules, []);
    assert.deepStrictEqual(store.learningPaths, []);
  });

  it("con token pero sin usuario guardado, user queda null", () => {
    installLocalStorage({ token: "tok-guardado" });
    const store = initialStore();
    assert.strictEqual(store.token, "tok-guardado");
    assert.strictEqual(store.user, null);
  });

  it("sin localStorage (entorno Node puro) lanza ReferenceError: documenta el acoplamiento", () => {
    delete globalThis.localStorage;
    assert.throws(() => initialStore(), ReferenceError);
  });
});
