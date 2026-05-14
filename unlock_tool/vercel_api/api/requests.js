const { redis } = require("../lib/redis");

module.exports = async function handler(req, res) {
  if (req.method !== "GET") return res.status(405).end();

  const ids = await redis("SMEMBERS", "pending");
  if (!ids || ids.length === 0) return res.json([]);

  const records = await Promise.all(
    ids.map(id => redis("GET", `req:${id}`).then(r => r ? (typeof r === "string" ? JSON.parse(r) : r) : null))
  );

  return res.json(
    records.filter(r => r && r.status === "pending").sort((a, b) => a.created_at - b.created_at)
  );
};
