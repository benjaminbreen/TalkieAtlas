const {test} = require('node:test');
const assert = require('node:assert/strict');
const handler = require('../api/stars.js');
const ids = require('../api/star-ids.json');
process.env.KV_REST_API_URL = 'https://example.test';
process.env.KV_REST_API_TOKEN = 'test-only';
const entries = new Map();
global.fetch = async (_url, opts) => {
  const cmd = JSON.parse(opts.body);
  let result;
  if (cmd[0] === 'HGETALL') result = [...entries].flat();
  else { const id = cmd[4], next = Math.max(0, (entries.get(id) || 0) + Number(cmd[5])); if (next) entries.set(id,next); else entries.delete(id); result = next; }
  return {ok:true, json:async () => ({result})};
};
async function call(method, body, headers = {}) {
  const res = {headers:{},setHeader(k,v){this.headers[k]=v;},status(v){this.code=v;return this;},json(v){this.body=v;return this;}};
  await handler({method,body,headers:{host:'localhost:8946','content-type':'application/json',...headers}},res);
  return res;
}
test('aggregate star counts increment, unstar, and never go negative', async () => {
  assert.equal((await call('POST',{id:ids[0],delta:1})).body.count,1);
  assert.equal((await call('POST',{id:ids[0],delta:1})).body.count,2);
  assert.equal((await call('GET')).body.counts[ids[0]],2);
  assert.equal((await call('POST',{id:ids[0],delta:-1})).body.count,1);
  assert.equal((await call('POST',{id:ids[0],delta:-1})).body.count,0);
  assert.equal((await call('POST',{id:ids[0],delta:-1})).body.count,0);
  assert.deepEqual((await call('GET')).body.counts,{});
});
test('reject unknown entries, invalid increments, cross-origin writes and malformed requests',async () => {
  for (const body of [{id:'unknown',delta:1},{id:ids[0],delta:100},{id:ids[0],delta:'1'},null,'{']) assert.equal((await call('POST',body)).code,400);
  assert.equal((await call('POST',{id:ids[0],delta:1},{origin:'https://other.example'})).code,403);
  assert.equal((await call('POST',{id:ids[0],delta:1},{'content-type':'text/plain'})).code,415);
  assert.equal((await call('DELETE')).code,405);
  assert.equal((await call('POST',{id:ids[0],delta:1},{'content-length':'9999'})).code,413);
});
test('storage failure reports an error without pretending a star was saved', async () => {
  const original=global.fetch; global.fetch=async()=>{throw Error('offline');};
  assert.equal((await call('POST',{id:ids[0],delta:1})).code,503); global.fetch=original;
});
