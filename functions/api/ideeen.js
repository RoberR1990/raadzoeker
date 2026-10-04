// Ideeënlijst met stemmen (Cloudflare Pages Function, D1-binding 'DB').
// Wie je bent komt uit Cloudflare Access (header Cf-Access-Authenticated-User-Email); we slaan alleen een hash op.
// Regels: maximaal 3 stemmen per persoon op ideeën die nog niet gebouwd zijn; een stem kun je intrekken en verplaatsen;
// is een idee gebouwd, dan telt die stem niet meer mee en komt hij vrij.
//   GET  /api/ideeen                     -> {ideeen:[{id,titel,toelichting,status,stemmen,mijn}], vrij}
//   POST /api/ideeen {actie:'stem'|'trek', id}
const MAX = 3;
async function wie(request) {
  const mail = (request.headers.get('Cf-Access-Authenticated-User-Email') || '').trim().toLowerCase();
  if (!mail) return null;
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('raadzoeker:' + mail));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}
const json = (x, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
async function lijst(db, g) {
  const { results } = await db.prepare(
    `SELECT i.id, i.titel, i.toelichting, i.status, COUNT(s.gebruiker) AS stemmen,
            SUM(CASE WHEN s.gebruiker = ?1 THEN 1 ELSE 0 END) AS mijn
       FROM ideeen i LEFT JOIN stemmen s ON s.idee_id = i.id
      GROUP BY i.id ORDER BY i.volgorde, i.id`).bind(g || '').all();
  const gebruikt = results.filter(r => r.mijn && r.status !== 'gebouwd').length;
  return { ideeen: results.map(r => ({ ...r, mijn: !!r.mijn })), vrij: g ? MAX - gebruikt : 0, ingelogd: !!g };
}
export async function onRequestGet({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database gekoppeld' }, 503);
  return json(await lijst(env.DB, await wie(request)));
}
export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database gekoppeld' }, 503);
  const g = await wie(request);
  if (!g) return json({ fout: 'niet ingelogd' }, 401);
  let b; try { b = await request.json(); } catch { return json({ fout: 'ongeldig verzoek' }, 400); }
  const id = Number(b.id);
  const idee = await env.DB.prepare('SELECT status FROM ideeen WHERE id = ?1').bind(id).first();
  if (!idee) return json({ fout: 'onbekend idee' }, 404);
  if (b.actie === 'trek') {
    await env.DB.prepare('DELETE FROM stemmen WHERE idee_id = ?1 AND gebruiker = ?2').bind(id, g).run();
  } else if (b.actie === 'stem') {
    if (idee.status === 'gebouwd') return json({ fout: 'dit idee is al gebouwd' }, 409);
    const l = await lijst(env.DB, g);
    if (l.vrij <= 0) return json({ fout: 'je hebt al ' + MAX + ' stemmen gebruikt; trek er eerst een in' }, 409);
    await env.DB.prepare('INSERT OR IGNORE INTO stemmen (idee_id, gebruiker, moment) VALUES (?1, ?2, ?3)').bind(id, g, new Date().toISOString()).run();
  } else return json({ fout: 'onbekende actie' }, 400);
  return json(await lijst(env.DB, g));
}
