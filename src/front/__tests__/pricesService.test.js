// Tests de src/front/services/pricesService.js con node --test,
// sin dependencias nuevas. El módulo no usa import.meta ni APIs de
// navegador: solo fetch global, que aquí se simula por test y se
// restaura al terminar. Ejecutar desde la raíz del repo:
//   node --test "src/front/__tests__/*.test.js"
import { describe, it, afterEach } from "node:test";
import assert from "node:assert/strict";
import { getPrices } from "../services/pricesService.js";

const realFetch = globalThis.fetch;

const stubFetchOk = (data, captured) => {
  globalThis.fetch = async (url) => {
    if (captured) captured.url = url;
    return { ok: true, status: 200, json: async () => data };
  };
};

describe("getPrices", () => {
  afterEach(() => {
    globalThis.fetch = realFetch;
  });

  it("mapea la respuesta de CoinGecko a symbol/price/change en el orden fijo de monedas", async () => {
    stubFetchOk({
      zcash: { usd: 40, usd_24h_change: 0.5 },
      bitcoin: { usd: 50000, usd_24h_change: 2.5 },
      ethereum: { usd: 3000, usd_24h_change: -1.25 },
      solana: { usd: 150, usd_24h_change: 4 },
      binancecoin: { usd: 600, usd_24h_change: 1 },
      ripple: { usd: 0.6, usd_24h_change: -0.3 },
      hyperliquid: { usd: 25, usd_24h_change: 7.7 }
    });
    const prices = await getPrices();
    assert.deepStrictEqual(
      prices.map((p) => p.symbol),
      ["BTC", "ETH", "SOL", "BNB", "XRP", "HYPE", "ZEC"]
    );
    assert.deepStrictEqual(prices[0], { symbol: "BTC", price: 50000, change: 2.5 });
    assert.deepStrictEqual(prices[2], { symbol: "SOL", price: 150, change: 4 });
  });

  it("filtra las monedas que no vengan en la respuesta", async () => {
    stubFetchOk({ bitcoin: { usd: 50000, usd_24h_change: 2.5 } });
    const prices = await getPrices();
    assert.deepStrictEqual(prices, [{ symbol: "BTC", price: 50000, change: 2.5 }]);
  });

  it("con respuesta vacía devuelve un array vacío", async () => {
    stubFetchOk({});
    assert.deepStrictEqual(await getPrices(), []);
  });

  it("pide la URL de CoinGecko con ids, vs_currencies=usd y cambio 24h", async () => {
    const captured = {};
    stubFetchOk({}, captured);
    await getPrices();
    assert.ok(captured.url.startsWith("https://api.coingecko.com/api/v3/simple/price?"));
    assert.ok(captured.url.includes("ids=bitcoin,ethereum,solana,binancecoin,ripple,hyperliquid,zcash"));
    assert.ok(captured.url.includes("vs_currencies=usd"));
    assert.ok(captured.url.includes("include_24hr_change=true"));
  });

  it("si CoinGecko responde no-OK, lanza Error con el estado HTTP", async () => {
    globalThis.fetch = async () => ({ ok: false, status: 500, json: async () => ({}) });
    await assert.rejects(() => getPrices(), { message: "CoinGecko respondió 500" });
  });
});
