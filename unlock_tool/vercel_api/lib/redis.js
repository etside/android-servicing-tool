// Upstash Redis REST helper — no SDK, pure fetch
const URL  = process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN;

async function redis(...args) {
  const res = await fetch(`${URL}/${args.map(encodeURIComponent).join('/')}`, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  const json = await res.json();
  return json.result;
}

module.exports = { redis };
