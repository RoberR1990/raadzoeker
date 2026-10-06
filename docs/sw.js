// Service worker van raadzoeker: alleen voor pushmeldingen over gevolgde onderwerpen (geen offline-cache).
// De push zelf is leeg; de tekst haalt de worker op bij /api/push?id=<hash van het push-adres>.
const hex = (buf) => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
self.addEventListener('push', (e) => {
  e.waitUntil((async () => {
    let b = { titel: 'raadzoeker', tekst: 'Er is nieuws in wat je volgt.', link: '/ontwerp/volg.html' };
    try {
      const sub = await self.registration.pushManager.getSubscription();
      if (sub) { const id = hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(sub.endpoint))); b = await (await fetch('/api/push?id=' + id)).json(); }
    } catch (x) {}
    await self.registration.showNotification(b.titel, { body: b.tekst, icon: '/ontwerp/logo.svg', badge: '/ontwerp/logo.svg', data: { link: b.link || '/ontwerp/volg.html' }, tag: 'raadzoeker-volg' });
  })());
});
self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data && e.notification.data.link || '/ontwerp/volg.html'));
});
