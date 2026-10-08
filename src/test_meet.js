/* Test van de meetlaag (docs/meet.js) met jsdom: geen browser nodig, geen netwerk.
   Eenmalig:  npm install --no-save jsdom        (in src/js, of elders; zet dan NODE_PATH naar die node_modules)
   Draaien:   node src/test_meet.js
   Controleert: virtuele paden, privacyfilter vóór verzenden, klik-/toggle-gebeurtenissen, filters uit de hash, uitschakelen
   (?meet=uit, Do Not Track, ander domein), het laden van de tracker met de juiste instellingen, wachtrij en privacytekst op Over. */
const fs = require('fs'), path = require('path'), assert = require('assert');
const { JSDOM } = require('jsdom');
const ONT = path.join(__dirname, '..', 'docs');
const PROD = fs.readFileSync(path.join(ONT, 'meet.js'), 'utf8');   // productieconfig
const LEEG = s => s.replace(/(const CONF=\{[\s\S]*?)host:'[^']*'/, "$1host:''").replace(/(const CONF=\{[\s\S]*?)\bid:'[^']*'/, "$1id:''");
const MEET = LEEG(PROD);   // alle tests gaan uit van een lege config, tenzij ze AAN gebruiken
const ONTW = fs.readFileSync(path.join(ONT, 'ontwerp.js'), 'utf8');
const STUB = ONTW.split('\n').find(l => l.startsWith('window.rzMeet=window.rzMeet||'));
assert(STUB, 'stub in ontwerp.js ontbreekt');
const AAN = MEET.replace("host:''", "host:'https://stats.test'").replace("id:''", "id:'site-123'");
assert(AAN !== MEET, 'CONF niet gevonden in meet.js');
assert(/host:''/.test(MEET) && /\bid:''/.test(MEET), 'LEEG() maakt de config niet leeg');

let ok = 0, fout = 0;
const t = (naam, f) => { try { f(); ok++; console.log('OK   ' + naam); } catch (e) { fout++; console.log('FOUT ' + naam + ' :: ' + e.message); } };
const ta = async (naam, f) => { try { await f(); ok++; console.log('OK   ' + naam); } catch (e) { fout++; console.log('FOUT ' + naam + ' :: ' + e.message); } };
const wacht = ms => new Promise(r => setTimeout(r, ms));
const egal = (a, b, m) => assert.strictEqual(JSON.stringify(a), JSON.stringify(b), m);   // JSON: arrays uit het jsdom-venster zijn een andere realm

/* maakt een pagina en voert (optioneel eerst de stub en dan) meet.js uit */
function pagina(url, { body = '', ls = {}, dnt = false, bron = MEET, stub = true, voor = null } = {}) {
  const dom = new JSDOM(`<!doctype html><html><head><title>x</title></head><body>${body}</body></html>`, { url, runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window;
  for (const [k, v] of Object.entries(ls)) w.localStorage.setItem(k, v);
  if (dnt) Object.defineProperty(w.navigator, 'doNotTrack', { value: '1', configurable: true });
  if (stub) w.eval(STUB);
  if (voor) voor(w);
  w.eval(bron);
  return w;
}
const log = w => w.rzMeet.log;
const klik = (w, el) => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));
const namen = w => log(w).map(x => x[0]);
const BASIS = 'https://raadzoeker.nl/';

(async () => {
  /* ---- productieconfig ---- */
  t('productieconfig: Umami Cloud, geldig website-id, alleen raadzoeker.nl', () => {
    const c = PROD.match(/const CONF=\{([\s\S]*?)\};/)[1];
    assert(/host:'https:\/\/cloud\.umami\.is'/.test(c), 'host');
    assert(/\bid:'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'/.test(c), 'website-id is geen uuid');
    assert(/domeinen:'raadzoeker\.nl'/.test(c), 'domeinen');
    assert(/script:'script\.js'/.test(c), 'script');
  });

  /* ---- uit zolang er geen host en id is ---- */
  t('zonder host/id: niets actief, rzMeet is een veilige no-op', () => {
    const w = pagina(BASIS + 'dossier.html#parkeren');
    assert.strictEqual(w.rzMeet.actief, false);
    w.rzMeet('iets', { a: 1 });
    assert.strictEqual(w.document.querySelectorAll('script[src]').length, 0);
    assert.strictEqual(log(w).length, 0);
  });

  /* ---- virtueel pad ---- */
  t('virtueel pad: slug-pagina\'s en hash-routes', () => {
    const w = pagina(BASIS + 'dossier.html#parkeren');
    const rij = [
      ['/dossier.html', '#parkeren/tijdlijn', '/dossier/parkeren'],
      ['/dossier.html', '', '/dossiers'],
      ['/wijk.html', '#w-feijenoord', '/wijk/feijenoord'],
      ['/wijk.html', '#delfshaven', '/gebied/delfshaven'],
      ['/wijk.html', '', '/gebieden'],
      ['/briefing.html', '#abc-def', '/briefing/abc-def'],
      ['/zoek.html', '#q=jan+jansen&tab=stukken', '/zoeken'],
      ['/index.html', '', '/'],
      ['/startpagina.html', '', '/'],
      ['/', '', '/'],
      ['/domeinen.html', '', '/dossiers'],
      ['/lab.html', '#d=parkeren', '/inzichten'],
      ['/vergadering.html', '#ap-3', '/vergadering'],
      ['/verkenner.html', '', '/verkenner'],
      ['/dossier.html', '#../../etc/passwd', '/dossier/']
    ];
    for (const [p, h, verwacht] of rij) assert.strictEqual(w.rzMeet.pad(p, h), verwacht, `${p}${h}`);
  });
  t('virtueel pad: alleen utm-parameters blijven staan, nooit q', () => {
    const w = pagina(BASIS + 'zoek.html?q=geheim+dossier&utm_source=deel&utm_medium=teams&x=1#q=geheim');
    assert.strictEqual(w.rzMeet.virtueel(), '/zoeken?utm_source=deel&utm_medium=teams');
  });

  /* ---- privacyfilter vlak voor verzenden ---- */
  t('voor verzenden: url, titel en eigen referrer worden schoongemaakt', () => {
    const w = pagina(BASIS + 'zoek.html?q=jan+jansen#b=abc~3~jan-jansen');
    const p = w.rzMeetVoorVerzenden('event', { url: '/zoek.html?q=jan+jansen#b=x', title: 'Zoeken: jan jansen', referrer: 'https://raadzoeker.nl/zoek.html?q=jan', name: 'zoek' });
    assert.strictEqual(p.url, '/zoeken');
    assert.strictEqual(p.title, '/zoeken');
    assert.strictEqual(p.referrer, 'https://raadzoeker.nl/zoeken');
    assert.strictEqual(p.name, 'zoek');
    const e = w.rzMeetVoorVerzenden('event', { referrer: 'https://www.google.com/search?q=raadzoeker' });
    assert.strictEqual(e.referrer, 'https://www.google.com/search?q=raadzoeker', 'externe referrer blijft intact');
    assert.strictEqual(w.rzMeetVoorVerzenden('event', null), null);
  });
  t('schoon(): e-mail, lange cijfers, lengte, NaN en aantal velden', () => {
    const w = pagina(BASIS + 'zoek.html');
    const o = w.rzMeet.schoon({ a: 'mail jan@example.nl nu', b: 'bsn 123456789 x', c: 'x'.repeat(300), d: NaN, e: true, f: 3.14159, g: null, h: '  ' });
    assert.strictEqual(o.a, 'mail [e-mail] nu');
    assert.strictEqual(o.b, 'bsn [nr] x');
    assert.strictEqual(o.c.length, 100);
    assert(!('d' in o) && !('g' in o) && !('h' in o));
    assert.strictEqual(o.e, true);
    assert.strictEqual(o.f, 3.14);
    const veel = {}; for (let i = 0; i < 30; i++) veel['k' + i] = i;
    assert.strictEqual(Object.keys(w.rzMeet.schoon(veel)).length, 12);
  });

  /* ---- gebeurtenissen uit klikken (debug-modus: alles in rzMeet.log) ---- */
  const DBG = { 'rz-meetdebug': '1' };
  await ta('klikken: kopieer, tabs, video, volgen, deel, uitgaand', async () => {
    const w = pagina(BASIS + 'zoek.html', { ls: DBG, body: `
      <button data-rzc="copilot" data-rzb="x" id="k1">Kopieer voor Copilot</button>
      <div id="tabs"><button data-tab="stukken" id="k2">Stukken</button></div>
      <button data-video="v1" data-sec="12" id="k3">Bekijk</button>
      <button data-volg="parkeren" aria-pressed="false" id="k4">Volg</button>
      <a href="mailto:?subject=x&body=y" id="k5">mail</a>
      <a href="https://teams.microsoft.com/share?href=z" id="k6">teams</a>
      <a href="https://wa.me/?text=z" id="k7">wa</a>
      <button class="kopie" id="k8">kopieer</button>
      <a href="https://gemeenteraad.rotterdam.nl/Agenda/Index/1" id="k9">ibabs</a>
      <a href="https://sdk.companywebcast.com/x" id="k10">video</a>
      <a href="/dossier.html#x" id="k11">intern</a>
      <details class="item" id="d1"><summary>x</summary>y</details>
      <details data-blok="gezegd" id="d2"><summary>x</summary>y</details>` });
    const $ = id => w.document.getElementById(id);
    klik(w, $('k1')); klik(w, $('k2')); klik(w, $('k3'));
    $('k4').setAttribute('aria-pressed', 'true'); klik(w, $('k4'));
    klik(w, $('k5')); klik(w, $('k6')); klik(w, $('k7')); klik(w, $('k8')); klik(w, $('k9')); klik(w, $('k10')); klik(w, $('k11'));
    for (const id of ['d1', 'd2']) { $(id).open = true; $(id).dispatchEvent(new w.Event('toggle')); }
    await wacht(120);
    const L = log(w).filter(x => x[0] !== 'pageview');
    const vind = (n, f = () => true) => L.find(x => x[0] === n && f(x[1]));
    assert(vind('kopieer', d => d.soort === 'copilot' && d.pagina === 'zoek'), 'kopieer');
    assert(vind('zoek_tab', d => d.tab === 'stukken'), 'zoek_tab');
    assert(vind('video'), 'video');
    assert(vind('volg', d => d.slug === 'parkeren' && d.aan === true), 'volg');
    for (const k of ['mail', 'teams', 'whatsapp', 'kopie']) assert(vind('deel', d => d.kanaal === k), 'deel ' + k);
    assert(vind('uitgaand', d => d.doel === 'ibabs-raad'), 'uitgaand ibabs');
    assert(vind('uitgaand', d => d.doel === 'video'), 'uitgaand video');
    assert.strictEqual(L.filter(x => x[0] === 'uitgaand').length, 2, 'alleen externe links tellen, niet mail/teams/wa/intern');
    assert(vind('uitklap', d => d.blok === 'gezegd'), 'uitklap');
    assert(vind('resultaat_open'), 'resultaat_open');
  });
  await ta('klikken: pagina-specifieke knoppen tellen alleen op hun eigen pagina', async () => {
    const lab = pagina(BASIS + 'lab.html', { ls: DBG, body: '<button data-kopieer="g3" id="a">k</button><button data-link="g3" id="b">l</button><button id="print">p</button>' });
    klik(lab, lab.document.getElementById('a')); klik(lab, lab.document.getElementById('b')); klik(lab, lab.document.getElementById('print'));
    assert(log(lab).some(x => x[0] === 'inzicht' && x[1].actie === 'afbeelding' && x[1].grafiek === 'g3'));
    assert(log(lab).some(x => x[0] === 'inzicht' && x[1].actie === 'link'));
    assert(!namen(lab).includes('briefing'), '#print telt alleen op briefing');
    const br = pagina(BASIS + 'briefing.html#parkeren', { ls: DBG, body: '<button id="print">p</button><button id="word">w</button>' });
    klik(br, br.document.getElementById('print')); klik(br, br.document.getElementById('word'));
    const b = log(br).filter(x => x[0] === 'briefing').map(x => x[1].actie + ':' + x[1].slug);
    egal(b, ['pdf:parkeren', 'word:parkeren']);
    const vk = pagina(BASIS + 'verkenner.html', { ls: DBG, body: '<button id="verras">v</button><button id="route">r</button><button id="foto">f</button><button data-a="deel">d</button>' });
    for (const id of ['verras', 'route', 'foto']) klik(vk, vk.document.getElementById(id));
    klik(vk, vk.document.querySelector('[data-a=deel]'));
    egal(log(vk).filter(x => x[0] === 'verkenner').map(x => x[1].actie), ['verras', 'route', 'afbeelding', 'deel']);
    const bl = pagina(BASIS + 'beloofd.html', { ls: DBG, body: '<button id="csv">csv</button>' });
    klik(bl, bl.document.getElementById('csv'));
    assert(namen(bl).includes('beloofd_csv'));
  });

  /* ---- filters uit de hash ---- */
  await ta('hash-filters: onderwerp-sleutels ja, zoekterm/spreker/fractie nee', async () => {
    const w = pagina(BASIS + 'lab.html#d=parkeren&f=pvv&q=geheim&spreker=jan&van=2022&k=grafiek', { ls: DBG });
    await wacht(900);
    const e = log(w).find(x => x[0] === 'weergave');
    assert(e, 'geen weergave-event');
    egal(e[1], { pagina: 'lab', d: 'parkeren', van: '2022', k: 'grafiek' });
    const z = pagina(BASIS + 'zoek.html#q=geheim', { ls: DBG });
    await wacht(900);
    assert(!namen(z).includes('weergave'), 'alleen een zoekterm geeft geen event');
  });
  await ta('paginaweergave: bij hashchange alleen als het virtuele pad verandert', async () => {
    const w = pagina(BASIS + 'dossier.html#parkeren', { ls: DBG });
    const pv = () => log(w).filter(x => x[0] === 'pageview').map(x => x[1]);
    egal(pv(), ['/dossier/parkeren']);
    w.location.hash = '#parkeren/tijdlijn'; await wacht(30);
    egal(pv(), ['/dossier/parkeren'], 'zelfde dossier telt niet dubbel');
    w.location.hash = '#wonen'; await wacht(30);
    egal(pv(), ['/dossier/parkeren', '/dossier/wonen']);
  });

  /* ---- uitzetten ---- */
  await ta('uitzetten: ?meet=uit, Do Not Track en ander domein laden de tracker niet', async () => {
    const uit = pagina(BASIS + 'dossier.html?meet=uit#parkeren', { bron: AAN });
    assert.strictEqual(uit.rzMeet.actief, false);
    assert.strictEqual(uit.localStorage.getItem('rz-nometen'), '1');
    assert.strictEqual(uit.localStorage.getItem('umami.disabled'), '1');
    assert.strictEqual(uit.document.querySelectorAll('script[src]').length, 0);
    const dnt = pagina(BASIS + 'dossier.html#parkeren', { bron: AAN, dnt: true });
    assert.strictEqual(dnt.rzMeet.actief, false);
    assert.strictEqual(dnt.document.querySelectorAll('script[src]').length, 0);
    const lokaal = pagina('http://localhost:8765/dossier.html#parkeren', { bron: AAN });
    assert.strictEqual(lokaal.rzMeet.actief, false);
    const terug = pagina(BASIS + 'dossier.html?meet=aan#parkeren', { bron: AAN, ls: { 'rz-nometen': '1', 'umami.disabled': '1' } });
    assert.strictEqual(terug.rzMeet.actief, true, '?meet=aan zet het weer aan');
  });

  /* ---- actief: tracker laden, wachtrij, paginaweergave ---- */
  await ta('actief: script met de juiste instellingen; wachtrij en pageview na het laden', async () => {
    const w = pagina(BASIS + 'zoek.html?q=geheim#q=geheim', { bron: AAN, voor: w => { w.rzMeet('vroeg', { x: 1 }); } });
    const s = w.document.querySelector('script[src]');
    assert(s, 'tracker niet geladen');
    assert.strictEqual(s.getAttribute('src'), 'https://stats.test/script.js');
    const d = s.dataset;
    assert.strictEqual(d.websiteId, 'site-123');
    assert.strictEqual(d.autoPageview, 'false');
    assert.strictEqual(d.domains, 'raadzoeker.nl');
    assert.strictEqual(d.doNotTrack, 'true');
    assert.strictEqual(d.excludeSearch, 'true');
    assert.strictEqual(d.excludeHash, 'true');
    assert.strictEqual(d.beforeSend, 'rzMeetVoorVerzenden');
    assert.strictEqual(typeof w.rzMeetVoorVerzenden, 'function');
    const verstuurd = [];
    w.umami = { track: (...a) => verstuurd.push(a) };
    w.rzMeet('na-bijna', { y: 2 });                       // tracker nog niet 'geladen': wachtrij
    assert.strictEqual(verstuurd.length, 0);
    s.onload();
    const namenV = verstuurd.map(a => typeof a[0] === 'function' ? 'pageview' : a[0]);
    egal(namenV, ['pageview', 'vroeg', 'na-bijna']);
    const pv = verstuurd[0][0]({ url: '/zoek.html?q=geheim#q=geheim', title: 'Zoeken', website: 'site-123' });
    assert.strictEqual(pv.url, '/zoeken');
    assert.strictEqual(pv.website, 'site-123', 'standaardvelden blijven bewaard');
    w.rzMeet('daarna');
    assert.strictEqual(verstuurd[3][0], 'daarna');
  });

  /* ---- Over: privacytekst en keuze ---- */
  await ta('Over: privacytekst alleen bij actieve meting, knop schakelt', async () => {
    const body = '<ul><li id="meetpriv" hidden></li></ul><p>Zo zien we.<span id="meetfaq" hidden></span></p>';
    const uit = pagina(BASIS + 'over.html', { body });
    await wacht(60);
    assert.strictEqual(uit.document.getElementById('meetpriv').hidden, true);
    assert.strictEqual(uit.document.getElementById('meetfaq').hidden, true);
    const aan = pagina(BASIS + 'over.html', { body, bron: AAN });
    await wacht(60);
    const li = aan.document.getElementById('meetpriv');
    assert.strictEqual(li.hidden, false);
    assert(/Umami/.test(li.textContent) && /Umami Cloud/.test(li.textContent));
    assert.strictEqual(aan.document.getElementById('meetfaq').hidden, false);
    const kn = aan.document.getElementById('meetknop');
    assert.strictEqual(kn.textContent, 'Mijn bezoeken niet meetellen');
    klik(aan, kn);
    assert.strictEqual(aan.localStorage.getItem('rz-nometen'), '1');
    assert.strictEqual(kn.textContent, 'Weer meetellen');
    klik(aan, kn);
    assert.strictEqual(aan.localStorage.getItem('rz-nometen'), null);
    const dnt = pagina(BASIS + 'over.html', { body, bron: AAN, dnt: true });
    await wacht(60);
    assert(!dnt.document.getElementById('meetknop'), 'bij Do Not Track geen knop');
    assert(/respecteren/.test(dnt.document.getElementById('meetpriv').textContent));
  });

  /* ---- gepatchte bronbestanden: bestaan de haken nog en is de syntaxis goed ---- */
  t('haken in bestaande code aanwezig', () => {
    const lees = f => fs.readFileSync(path.join(ONT, f), 'utf8');
    assert(/rzMeet\('fout_open'/.test(ONTW) && /rzMeet\('fout_gemeld'/.test(ONTW), 'fout melden');
    assert(/metUtm\(url,'?k?/.test(ONTW) && ONTW.includes("uk('teams')") && ONTW.includes("uk('whatsapp')") && ONTW.includes("uk('mail')"), 'deellinks met utm');
    assert(lees('zoek.html').includes("rzMeet('zoek',{n,leeg:n===0"), 'zoek');
    assert(lees('stad.js').includes("rzMeet('ei'"), 'easter eggs');
    const tour = lees('tour.js');
    for (const x of ["actie:'start'", "actie:'klaar'", "actie:'stop'", "rzMeet('welkom'"]) assert(tour.includes(x), 'tour ' + x);
    assert(/m\.src='meet\.js\?v=\d+'/.test(ONTW), 'meet.js wordt geladen door kop()');
    assert(lees('over.html').includes('id="meetpriv"') && lees('over.html').includes('id="meetfaq"'), 'over.html');
  });
  t('syntaxis: ontwerp.js, tour.js, stad.js, meet.js en de scripts in zoek.html/over.html', () => {
    const { Script } = require('vm');
    for (const f of ['ontwerp.js', 'tour.js', 'stad.js', 'meet.js']) new Script(fs.readFileSync(path.join(ONT, f), 'utf8'), { filename: f });
    for (const f of ['zoek.html', 'over.html']) {
      const h = fs.readFileSync(path.join(ONT, f), 'utf8');
      const blokken = [...h.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
      assert(blokken.length, f + ': geen inline script');
      blokken.forEach((b, i) => new Script(b, { filename: `${f}#${i}` }));
    }
  });
  t('alle pagina\'s met ontwerp.js gebruiken versie 41; deelpagina\'s sturen utm door', () => {
    const alle = [];
    (function loop(d) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) { if (!/[\\/]data$/.test(p)) loop(p); } else if (p.endsWith('.html')) alle.push(p); } })(ONT);
    const oud = alle.filter(f => /ontwerp\.js\?v=(?!41\b)\d+/.test(fs.readFileSync(f, 'utf8')));
    egal(oud, [], 'nog op een oude versie');
    const deel = fs.readdirSync(path.join(ONT, 'deel')).filter(f => f.endsWith('.html'));
    assert(deel.length > 50);
    const zonder = deel.filter(f => !fs.readFileSync(path.join(ONT, 'deel', f), 'utf8').includes('location.replace'));
    egal(zonder, [], 'deelpagina\'s zonder doorstuur-script');
  });

  console.log(`\n${ok} geslaagd, ${fout} mislukt`);
  process.exit(fout ? 1 : 0);
})();
