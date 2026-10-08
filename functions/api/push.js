// Pushmeldingen versturen (Cloudflare Pages Function, D1-binding 'DB').
//   POST /api/push  (body {vapid: privé-JWK, volg: volg.json}, alleen vanaf de NAS)  -> per abonnee: nieuw sinds de vorige melding? bericht klaarzetten + lege push
//   GET  /api/push?id=<sha256 van het push-adres>                 -> het klaargezette bericht (de service worker haalt dit op)
// Lege pushberichten: de inhoud gaat niet via de pushdienst, dus geen versleuteling nodig; alleen VAPID-ondertekening (ES256).
// De privésleutel staat alleen op de NAS en komt per verzending mee; hier wordt niets geheims bewaard. Wie de juiste sleutel
// (passend bij PUB) niet heeft, kan niets versturen.
const PUB = 'BCQ5wiH7FYmjbMIOViN3DznTaCF-4ClUMhS7n1KqXt4fFbNWBp947WtCU_nhCw-SugxSNpFqvyI-t3C-9DVSBiY';
const json = (x, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const tekst = (s) => b64u(new TextEncoder().encode(s));
const ub = (s) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4)), c => c.charCodeAt(0));
async function vapid(jwk, aud) {   // JWT voor deze pushdienst, 12 uur geldig
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'ECDSA', namedCurve: 'P-256' }, false, ['sign']);
  const kop = tekst(JSON.stringify({ typ: 'JWT', alg: 'ES256' }));
  const inh = tekst(JSON.stringify({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: 'https://raadzoeker.nl/over.html' }));
  const sig = await crypto.subtle.sign({ name: 'ECDSA', hash: 'SHA-256' }, key, new TextEncoder().encode(kop + '.' + inh));
  return kop + '.' + inh + '.' + b64u(sig);
}
export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database' }, 503);
  let body; try { body = await request.json(); } catch (e) { return json({ fout: 'ongeldig' }, 400); }
  const jwk = body.vapid || {}, volg = body.volg || {};
  let past = false; try { past = !!(jwk.d && jwk.x && jwk.y) && b64u(Uint8Array.from([4, ...ub(jwk.x), ...ub(jwk.y)])) === PUB; } catch (e) {}
  if (!past) return json({ fout: 'geen toegang' }, 403);
  const D = volg.d || {}, stand = volg.stand || new Date().toISOString().slice(0, 10), pub = PUB;
  const { results } = await env.DB.prepare('SELECT id, endpoint, onderwerpen, gemeld FROM abonnees').all();
  const jwts = {}; let verstuurd = 0, weg = 0;
  for (const a of results) {
    const ond = JSON.parse(a.onderwerpen || '[]'); const nieuw = [];
    for (const s of ond) for (const i of ((D[s] || {}).i || [])) if (i[0] > a.gemeld) nieuw.push([s, i]);
    if (!nieuw.length) continue;
    const namen = [...new Set(nieuw.map(([s]) => (D[s] || {}).naam || s))];
    const bericht = { titel: nieuw.length === 1 ? (D[nieuw[0][0]] || {}).naam || 'raadzoeker' : `Nieuw in ${namen.slice(0, 2).join(' en ')}${namen.length > 2 ? ' en meer' : ''}`,
      tekst: nieuw.length === 1 ? nieuw[0][1][2] : `${nieuw.length} nieuwe items, o.a. ${nieuw[0][1][2]}`.slice(0, 180), link: '/volg.html' };
    const aud = new URL(a.endpoint).origin; jwts[aud] = jwts[aud] || await vapid(jwk, aud);
    const r = await fetch(a.endpoint, { method: 'POST', headers: { TTL: '86400', Urgency: 'normal', Authorization: `vapid t=${jwts[aud]}, k=${pub}`, 'Content-Length': '0' } });
    if (r.status === 404 || r.status === 410) { await env.DB.prepare('DELETE FROM abonnees WHERE id = ?1').bind(a.id).run(); weg++; continue; }
    await env.DB.prepare('UPDATE abonnees SET gemeld = ?2, bericht = ?3 WHERE id = ?1').bind(a.id, stand, JSON.stringify(bericht)).run();
    if (r.ok) verstuurd++;
  }
  return json({ ok: true, abonnees: results.length, verstuurd, weg });
}
export async function onRequestGet({ request, env }) {
  if (!env.DB) return json({}, 503);
  const id = new URL(request.url).searchParams.get('id') || '';
  const r = /^[0-9a-f]{64}$/.test(id) ? await env.DB.prepare('SELECT bericht FROM abonnees WHERE id = ?1').bind(id).first() : null;
  return json(r && r.bericht ? JSON.parse(r.bericht) : { titel: 'raadzoeker', tekst: 'Er is nieuws in wat je volgt.', link: '/volg.html' });
}
