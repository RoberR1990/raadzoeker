// Volgen met pushmeldingen (Cloudflare Pages Function, D1-binding 'DB').
// Bewaard per browser: alleen het push-adres (van de browserdienst), de gevolgde dossiers en de dag. Geen naam, geen e-mail, geen IP-adres.
//   POST   /api/volg {endpoint, onderwerpen:[slug…]}  -> aanmelden of lijst bijwerken
//   DELETE /api/volg {endpoint}                       -> afmelden (alles weg)
const json = (x, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
// alleen bekende pushdiensten (voorkomt dat iemand de server naar willekeurige adressen laat sturen)
const MAX = 2000;
const DIENST = /^https:\/\/([a-z0-9-]+\.)*(fcm\.googleapis\.com|push\.services\.mozilla\.com|notify\.windows\.com|push\.apple\.com)\//;
export async function hash(s) { const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)); return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join(''); }
async function lees(request) { try { return await request.json(); } catch (e) { return null; } }
export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database' }, 503);
  const b = await lees(request); const ep = String(b && b.endpoint || '');
  if (!DIENST.test(ep) || ep.length > 1000) return json({ fout: 'ongeldig adres' }, 400);
  const ond = [...new Set((Array.isArray(b.onderwerpen) ? b.onderwerpen : []).map(String).filter(s => /^[a-z0-9-]{1,80}$/.test(s)))].slice(0, 50);
  const dag = new Date().toISOString().slice(0, 10), id = await hash(ep);
  // tegen misbruik: hooguit 30 aanmeldingen/wijzigingen per dag per (gehasht) IP-adres, en niet meer dan MAX abonnees in totaal
  const sleutel = (await hash('volg:' + dag + ':' + (request.headers.get('CF-Connecting-IP') || ''))).slice(0, 24);
  const r = await env.DB.prepare('INSERT INTO limiet (sleutel, n) VALUES (?1, 1) ON CONFLICT(sleutel) DO UPDATE SET n = n + 1 RETURNING n').bind(sleutel).first();
  if (r && r.n > 30) return json({ fout: 'te veel' }, 429);
  if (ond.length && !(await env.DB.prepare('SELECT 1 FROM abonnees WHERE id = ?1').bind(id).first())) {
    const t = await env.DB.prepare('SELECT COUNT(*) AS n FROM abonnees').first();
    if (t && t.n >= MAX) return json({ fout: 'vol' }, 503);
  }
  if (!ond.length) { await env.DB.prepare('DELETE FROM abonnees WHERE id = ?1').bind(id).run(); return json({ ok: true, afgemeld: true }); }
  await env.DB.prepare(`INSERT INTO abonnees (id, endpoint, onderwerpen, sinds, gemeld) VALUES (?1, ?2, ?3, ?4, ?4)
    ON CONFLICT(id) DO UPDATE SET onderwerpen = ?3`).bind(id, ep, JSON.stringify(ond), dag).run();
  return json({ ok: true, n: ond.length });
}
export async function onRequestDelete({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database' }, 503);
  const b = await lees(request); const ep = String(b && b.endpoint || '');
  if (ep) await env.DB.prepare('DELETE FROM abonnees WHERE id = ?1').bind(await hash(ep)).run();
  return json({ ok: true });
}
