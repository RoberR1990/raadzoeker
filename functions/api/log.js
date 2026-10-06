// Anonieme zoeklog (Cloudflare Pages Function, D1-binding 'DB'): wat mensen zoeken en hoeveel het opleverde.
// Geen persoon, geen tijdstip: alleen de zoekopdracht (max 200 tekens), het aantal resultaten, de pagina en de dag.
//   POST /api/log {q, n, pagina}
export async function onRequestPost({ request, env }) {
  if (!env.DB) return new Response(null, { status: 204 });
  try {
    const b = await request.json();
    const q = String(b.q || '').trim().slice(0, 200);
    // tegen misbruik: hooguit 300 zoekopdrachten per dag per (gehasht) IP-adres; het adres zelf wordt niet bewaard
    const dag = new Date().toISOString().slice(0, 10);
    const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode('log:' + dag + ':' + (request.headers.get('CF-Connecting-IP') || '')));
    const sleutel = [...new Uint8Array(h)].slice(0, 12).map(x => x.toString(16).padStart(2, '0')).join('');
    const r = await env.DB.prepare('INSERT INTO limiet (sleutel, n) VALUES (?1, 1) ON CONFLICT(sleutel) DO UPDATE SET n = n + 1 RETURNING n').bind(sleutel).first();
    if (r && r.n > 300) return new Response(null, { status: 204 });
    if (q) await env.DB.prepare('INSERT INTO zoeklog (q, n, pagina, dag) VALUES (?1, ?2, ?3, ?4)')
      .bind(q, Number.isFinite(+b.n) ? +b.n : null, String(b.pagina || '').slice(0, 40), new Date().toISOString().slice(0, 10)).run();
  } catch (e) { /* loggen mag nooit de pagina breken */ }
  return new Response(null, { status: 204 });
}
