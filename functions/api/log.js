// Anonieme zoeklog (Cloudflare Pages Function, D1-binding 'DB'): wat mensen zoeken en hoeveel het opleverde.
// Geen persoon, geen tijdstip: alleen de zoekopdracht (max 200 tekens), het aantal resultaten, de pagina en de dag.
//   POST /api/log {q, n, pagina}
export async function onRequestPost({ request, env }) {
  if (!env.DB) return new Response(null, { status: 204 });
  try {
    const b = await request.json();
    const q = String(b.q || '').trim().slice(0, 200);
    if (q) await env.DB.prepare('INSERT INTO zoeklog (q, n, pagina, dag) VALUES (?1, ?2, ?3, ?4)')
      .bind(q, Number.isFinite(+b.n) ? +b.n : null, String(b.pagina || '').slice(0, 40), new Date().toISOString().slice(0, 10)).run();
  } catch (e) { /* loggen mag nooit de pagina breken */ }
  return new Response(null, { status: 204 });
}
