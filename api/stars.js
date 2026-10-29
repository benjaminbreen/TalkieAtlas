// Only aggregate counts are persisted. No accounts, cookies, IPs, or voter IDs.
const allowed = new Set(require('./star-ids.json'));
const hash = 'talkie-persona-library:stars:v1';
const update = `
local count = tonumber(redis.call('HGET', KEYS[1], ARGV[1]) or '0')
local next = math.max(0, count + tonumber(ARGV[2]))
if next == 0 then redis.call('HDEL', KEYS[1], ARGV[1])
else redis.call('HSET', KEYS[1], ARGV[1], next) end
return next`;

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  if (!['GET', 'POST'].includes(req.method)) {
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({error:'Method not allowed'});
  }
  let body;
  if (req.method === 'POST') {
    const origin = req.headers.origin;
    const host = req.headers.host;
    if (origin) {
      try { if (new URL(origin).host !== host) return res.status(403).json({error:'Origin not allowed'}); }
      catch { return res.status(403).json({error:'Origin not allowed'}); }
    }
    if (!/^application\/json(?:;|$)/i.test(req.headers['content-type'] || '')) return res.status(415).json({error:'JSON required'});
    if (Number(req.headers['content-length']) > 1024) return res.status(413).json({error:'Request too large'});
    try { body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body; }
    catch { return res.status(400).json({error:'Invalid request'}); }
    if (!body || !allowed.has(body.id) || ![1, -1].includes(body.delta)) return res.status(400).json({error:'Invalid persona or star change'});
  }
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  if (!url || !token) return res.status(503).json({error:'Stars unavailable'});
  try {
    const command = req.method === 'GET' ? ['HGETALL', hash] : ['EVAL', update, '1', hash, body.id, String(body.delta)];
    const response = await fetch(url, {method:'POST', headers:{Authorization:`Bearer ${token}`, 'Content-Type':'application/json'}, body:JSON.stringify(command), signal:AbortSignal.timeout(8000)});
    if (!response.ok) throw Error('Storage unavailable');
    const result = await response.json();
    if (result.error) throw Error('Storage unavailable');
    if (req.method === 'POST') return res.status(200).json({id:body.id, count:Number(result.result)});
    const counts = {};
    for (let i = 0; i < result.result.length; i += 2) {
      const id = result.result[i], count = Number(result.result[i + 1]);
      if (allowed.has(id) && Number.isSafeInteger(count) && count > 0) counts[id] = count;
    }
    return res.status(200).json({counts});
  } catch { return res.status(503).json({error:'Stars unavailable. Please try again.'}); }
};
