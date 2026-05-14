const { redis } = require("../../lib/redis");

module.exports = async function handler(req, res) {
  const { id } = req.query;
  if (!id) return res.status(400).json({ error: "missing id" });

  if (req.method === "GET") {
    const raw = await redis("GET", `req:${id}`);
    if (!raw) return res.status(404).json({ error: "not found" });
    return res.json(typeof raw === "string" ? JSON.parse(raw) : raw);
  }

  if (req.method === "PATCH") {
    const { status } = req.body || {};
    if (!["approved", "denied"].includes(status))
      return res.status(400).json({ error: "invalid status" });

    const raw = await redis("GET", `req:${id}`);
    if (!raw) return res.status(404).json({ error: "not found" });

    const record = typeof raw === "string" ? JSON.parse(raw) : raw;
    record.status = status;
    await redis("SET", `req:${id}`, JSON.stringify(record), "EX", "86400");
    await redis("SREM", "pending", id);

    return res.json({ ok: true });
  }

  return res.status(405).end();
};
