import type { Config, Context } from "@netlify/functions"
import { getStore } from "@netlify/blobs"

// One student, one snapshot. The app overwrites it after each study session;
// the dashboard reads it with Dad's PIN (set as the DAD_PIN env var).
const STORE = "act-progress"
const KEY = "yoseph"
const WRITE_TOKEN = "yoseph-act-sync-v1" // ships in the app; only stops random posts
const MAX_BYTES = 300_000

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
    // Dad's PIN lives only in the DAD_PIN environment variable (set in the Netlify UI).
    const pin = (Netlify.env.get("DAD_PIN") || "").trim()
    if (!pin) return json({ error: "The dashboard PIN isn't set up yet. Add DAD_PIN under Environment variables in Netlify, then redeploy." }, 503)
    const given = (req.headers.get("x-dad-pin") || "").trim()
    if (given !== pin) return json({ error: "Wrong PIN." }, 401)
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
