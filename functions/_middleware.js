// Domeinen: de site heet sinds 6-10-2026 De Publieke Tribune.
// De site is openbaar (besluit Robert 6-10-2026); de oude link stuurt door naar de nieuwe.
// (De oude link zit nog achter Cloudflare Access; wie daar inlogt, komt daarna op de nieuwe link.)
const OUD = 'raadzoeker.pages.dev', NIEUW = 'publieke-tribune.pages.dev', BESCHERMD = true;
export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  if (!BESCHERMD && url.hostname === NIEUW) { url.hostname = OUD; return Response.redirect(url.toString(), 302); }
  if (BESCHERMD && url.hostname === OUD) { url.hostname = NIEUW; return Response.redirect(url.toString(), 301); }
  return ctx.next();
}
