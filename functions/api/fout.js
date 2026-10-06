// Fout melden (Cloudflare Pages Function, D1-binding 'DB'). Geen persoon: alleen de pagina, waar het over gaat, de tekst en de dag.
// Tegen misbruik: hooguit 20 meldingen per dag per (gehasht) IP-adres; het IP-adres zelf wordt niet bewaard.
//   POST /api/fout {pagina, over, tekst}
const json = (x, status = 200) => new Response(JSON.stringify(x), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ fout: 'geen database' }, 503);
  let b; try { b = await request.json(); } catch (e) { return json({ fout: 'ongeldig' }, 400); }
  const tekst = String(b.tekst || '').trim().slice(0, 2000);
  if (tekst.length < 3) return json({ fout: 'leeg' }, 400);
  const dag = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get('CF-Connecting-IP') || '';
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('fout:' + dag + ':' + ip));
  const sleutel = [...new Uint8Array(h)].slice(0, 12).map(x => x.toString(16).padStart(2, '0')).join('');
  const r = await env.DB.prepare('INSERT INTO limiet (sleutel, n) VALUES (?1, 1) ON CONFLICT(sleutel) DO UPDATE SET n = n + 1 RETURNING n').bind(sleutel).first();
  if (r && r.n > 20) return json({ fout: 'te veel' }, 429);
  await env.DB.prepare('INSERT INTO meldingen (dag, pagina, over, tekst) VALUES (?1, ?2, ?3, ?4)')
    .bind(dag, String(b.pagina || '').slice(0, 300), String(b.over || '').slice(0, 500), tekst).run();
  return json({ ok: true });
}
