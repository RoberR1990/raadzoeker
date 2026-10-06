// Domeinen: de site heet sinds 6-10-2026 De Publieke Tribune.
// Zolang publieke-tribune.pages.dev nog niet achter Cloudflare Access staat, gaat dat adres naar de beschermde oude link.
// Daarna draaien: OUD -> NIEUW (zet BESCHERMD op true).
const OUD = 'raadzoeker.pages.dev', NIEUW = 'publieke-tribune.pages.dev', BESCHERMD = false;
export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  if (!BESCHERMD && url.hostname === NIEUW) { url.hostname = OUD; return Response.redirect(url.toString(), 302); }
  if (BESCHERMD && url.hostname === OUD) { url.hostname = NIEUW; return Response.redirect(url.toString(), 301); }
  return ctx.next();
}
