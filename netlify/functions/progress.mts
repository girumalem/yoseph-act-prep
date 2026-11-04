import type { Config, Context } from "@netlify/functions"
import { getStore } from "@netlify/blobs"

// One student, one snapshot. The app overwrites it after each study session;
// the dashboard reads it with Dad's PIN (set as the DAD_PIN env var).
const STORE = "act-progress"
const KEY = "yoseph"
const WRITE_TOKEN = "yoseph-act-sync-v1" // ships in the app; only stops random posts
const MAX_BYTES = 300_000
// SHA-256 of Dad's PIN. To change the PIN, set a DAD_PIN environment variable
// in Netlify (it takes priority) or replace this hash.
const PIN_SHA256 = "cff225afb4fc8ef8e7c210efcfddfce78d85538abadcfb7d61cd5d6af09fa455"

async function sha256(text: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text))
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("")
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  })

export default async (req: Request, context: Context) => {
  const store = getStore({ name: STORE, consistency: "strong" })

  if (req.method === "POST") {
    if (req.headers.get("x-sync-token") !== WRITE_TOKEN) return json({ error: "unauthorized" }, 401)
    const text = await req.text()
    if (text.length > MAX_BYTES) return json({ error: "too large" }, 413)
    let data: any
    try { data = JSON.parse(text) } catch { return json({ error: "bad json" }, 400) }
    if (!data || typeof data !== "object" || typeof data.act !== "object") return json({ error: "bad shape" }, 400)
    data.receivedAt = Date.now()
    await store.setJSON(KEY, data)
    return json({ ok: true, receivedAt: data.receivedAt })
  }

  if (req.method === "GET") {
    const given = (req.headers.get("x-dad-pin") || "").trim()
    const envPin = Netlify.env.get("DAD_PIN")
    const ok = given !== "" && (envPin ? given === envPin : (await sha256(given)) === PIN_SHA256)
    if (!ok) return json({ error: "Wrong PIN." }, 401)
    const data = await store.get(KEY, { type: "json" })
    if (data === null) return json({ empty: true })
    return json(data)
  }

  return json({ error: "method not allowed" }, 405)
}

export const config: Config = {
  path: "/api/progress",
  method: ["GET", "POST"],
  rateLimit: { windowLimit: 15, windowSize: 60, aggregateBy: ["ip", "domain"] },
}
