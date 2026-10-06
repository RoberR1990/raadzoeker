// Domein: raadzoeker.nl is het hoofdadres (sinds 6-10-2026). Andere adressen sturen daarheen door, met behoud van pad en zoekopdracht.
// (raadzoeker.pages.dev zit nog achter Cloudflare Access; wie daar inlogt, komt daarna op raadzoeker.nl.)
const HOOFD = 'raadzoeker.nl';
const OUD = new Set(['www.raadzoeker.nl', 'publieke-tribune.pages.dev', 'raadzoeker.pages.dev']);
export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  if (OUD.has(url.hostname)) { url.hostname = HOOFD; return Response.redirect(url.toString(), 301); }
  return ctx.next();
}
