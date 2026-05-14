const { randomUUID } = require("crypto");
const { redis } = require("../../lib/redis");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  const { machine_id, user_ip, hostname } = req.body || {};
  if (!machine_id || !user_ip) return res.status(400).json({ error: "missing fields" });

  const id = randomUUID();
  const record = JSON.stringify({ id, machine_id, user_ip, hostname: hostname || "", status: "pending", created_at: Date.now() });

  await redis("SET", `req:${id}`, record, "EX", "86400");
  await redis("SADD", "pending", id);

  return res.status(201).json({ id });
};
