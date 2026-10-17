# Elders (17-10-2026): andere gemeenten naast een Rotterdams dossier. Geen AI.
#   python src/elders.py [slug ...]   -> docs/d/elders/<slug>.json + docs/d/elders/index.json
# Bronnen
#   moties   Open Raadsinformatie (Elasticsearch, api.openraadsinformatie.nl). Per gemeente een eigen naamregel (src/elders_bron.json,
#            bepaald in fase 0, zie ontwerp/elders/). Een motie hoort bij een dossier als het onderwerp in de titel staat of
#            minstens 2x in de tekst. Geen uitslag: die staat niet in ORI.
#   regels   CVDR (lokaleregelgeving.overheid.nl): de geldende regelingen per gemeente en dossier, vastgelegd in elders_bron.json
#            (momentopname; opnieuw bepalen met ontwerp/elders/).
# Werkt zonder werkmap; leest en schrijft alleen in docs/.
import json, os, re, sys, time, urllib.request
from paden import DOCS

HIER = os.path.dirname(os.path.abspath(__file__))
ORI = 'https://api.openraadsinformatie.nl/v1/elastic/'
SINDS = '2022-01-01'
MAX = 300   # moties per gemeente per dossier

# Per dossier: zoekvraag voor ORI (query_string op naam en tekst) en de controle-regex (op kleine letters).
DOSSIER = {
    'parkeren': dict(q='parkeer* OR parkeren OR naheffing OR bewonersvergunning OR bezoekersregeling',
                     rx=r'parkeer|parkeren|naheffing|bewonersvergunning|bezoekersregeling'),
    'handhaving-en-toezicht': dict(q="handhav* OR boa OR boa's OR toezichthouder* OR \"bestuurlijke strafbeschikking\" OR \"bestuurlijke boete\" OR bodycam*",
                     rx=r"handhav|\bboa\b|\bboa's|toezichthouder|bestuurlijke strafbeschikking|bestuurlijke boete|bodycam"),
    'deelscooters-en-deelfietsen': dict(q='deelscooter* OR deelfiets* OR deelmobiliteit OR deelvervoer OR deelauto* OR deelbakfiets* OR deeltweewieler*',
                     rx=r'deelscooter|deelfiets|deelmobiliteit|deelvervoer|deelauto|deelbakfiets|deeltweewieler'),
}


def haal(req, n=4):
    for i in range(n):
        try:
            return urllib.request.urlopen(req, timeout=120).read()
        except OSError:
            if i == n - 1:
                raise
            time.sleep(2 ** (i + 1))


def ori(idx, body):
    r = urllib.request.Request(ORI + idx + '/_search', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(haal(r))


def tekst(s):
    t = s.get('text') or ''
    return ' '.join(t) if isinstance(t, list) else t


UITSLAG = r'aangenomen|verworpen|ingetrokken|aangehouden|vervallen'
# uitslag in de tekst (fase 0): Eindhoven slotregel, Amsterdam/Den Haag kopblok bovenaan het stuk
TEKST_UITSLAG = {
    'eindhoven': r'deze (?:vrije )?(?:motie|amendement) is (aangenomen|verworpen|ingetrokken)',
    'amsterdam': r'^.{0,400}?\b(aangenomen|verworpen|ingetrokken)\b',
    'den_haag': r'(?:uitslag stemming:?\s*|^.{0,400}?\b)(aangenomen|verworpen|ingetrokken|aangehouden)\b',
}
STAT = re.compile(r'\s*[-–(]?\s*\b(?:aangenomen|verworpen|ingetrokken(?: na toezegging)?|aangehouden|gewijzigd|getekend|aangepast|vervallen)\b\)?\s*', re.I)


DICTUM = re.compile(r'verzoekt|draagt [^.]{0,40}op|roept [^.]{0,40}op|besluit|spreekt uit')


def over(t, orx):
    # alleen uit de tekst: minstens 3 keer genoemd en ook in het verzoek zelf (niet alleen in de overwegingen)
    if len(orx.findall(t)) < 3:
        return False
    m = DICTUM.search(t)
    return bool(m and orx.search(t, m.start()))


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', STAT.sub(' ', t.lower())).strip()


def moties(g, cfg, dos):
    if cfg.get('geen_moties'):
        return []
    body = {'size': MAX, '_source': ['name', 'last_discussed_at', 'original_url', 'text'],
            'sort': [{'last_discussed_at': 'desc'}],
            'query': {'bool': {'must': [cfg['ori_query'], {'query_string': {'query': dos['q'], 'fields': ['name', 'text']}}]}}}
    h = ori(f"ori_{g}_2*", body)['hits']['hits']
    mrx, arx = re.compile(cfg['motie_rx'], re.I), re.compile(cfg.get('amendement_rx') or r'(?!x)x', re.I)
    urx = re.compile(cfg['uitsluit_rx'], re.I) if cfg.get('uitsluit_rx') else None
    trx = [re.compile(r, re.I) for r in cfg.get('titel_rx') or []]
    unx = re.compile(cfg['uitslag_naam_rx'], re.I) if cfg.get('uitslag_naam_rx') else None
    ttx = re.compile(TEKST_UITSLAG[g], re.I | re.S) if g in TEKST_UITSLAG else None
    orx = re.compile(dos['rx'])
    uit = {}
    for x in h:
        s = x['_source']; naam = re.sub(r'\.(pdf|docx?)$', '', (s.get('name') or '').strip(), flags=re.I)
        soort = 'amendement' if arx.search(naam) else 'motie' if mrx.search(naam) else None
        if not soort or (urx and urx.search(naam)):
            continue
        tk = tekst(s)
        in_naam = bool(orx.search(naam.lower()))
        if not (in_naam or over(tk.lower(), orx)):
            continue
        titel, ind, us = naam, '', ''
        for r in trx:
            m = r.search(naam)
            if m:
                gd = m.groupdict()
                titel = (gd.get('titel') or naam).strip(' -–.:')
                ind = (gd.get('indieners') or '').strip(' -–.()')
                us = next((gd[k] for k in ('uitslag', 'uitslag0', 'uitslag1') if gd.get(k)), '') or ''
                break
        if not us and unx:
            m = unx.search(naam); us = m.group(1) if m else ''
        if not us and ttx:
            m = ttx.search(tk[:4000] if g != 'eindhoven' else tk[-3000:]); us = m.group(1) if m else ''
        us = us.lower() if re.fullmatch(UITSLAG, us.lower() or 'x') else ''
        titel = STAT.sub(' ', titel).strip(' -–.:') if re.search(r'\s[-–(]\s*(?:%s)\)?\s*$' % UITSLAG, titel, re.I) else titel
        titel = re.sub(r'\.(pdf|docx?)\s*$', '', titel, flags=re.I).strip()
        if len(titel) < 4:
            continue
        d = (s.get('last_discussed_at') or '')[:10]
        k = norm(titel)
        o = uit.get(k)
        if o:   # dezelfde motie in meerdere vergaderingen of versies: nieuwste datum, uitslag als die ergens staat
            o['uitslag'] = o['uitslag'] or us
            continue
        uit[k] = dict(datum=d, soort=soort, titel=titel, indieners=ind, uitslag=us, url=s.get('original_url') or '')
        if not orx.search(titel.lower()) and not in_naam:
            uit[k]['tekst'] = 1   # alleen in de tekst genoemd: steekproef 17-10-2026 zwak (8 van 38 duidelijk raak), apart tonen
    return sorted(uit.values(), key=lambda m: m['datum'], reverse=True)


def stand_ori(g):
    a = ori(f"ori_{g}_2*", {'size': 0, 'query': {'term': {'@type': 'Meeting'}}, 'aggs': {'mx': {'max': {'field': 'start_date'}}}})
    return (a['aggregations']['mx'].get('value_as_string') or '')[:10]


def main(slugs):
    B = json.load(open(os.path.join(HIER, 'elders_bron.json'), encoding='utf8'))
    G, R = B['gemeenten'], B['regels']
    slugs = slugs or list(DOSSIER)
    uitmap = os.path.join(DOCS, 'd', 'elders'); os.makedirs(uitmap, exist_ok=True)
    so = {g: stand_ori(g) for g in G}
    ip = os.path.join(uitmap, 'index.json')
    index = json.load(open(ip, encoding='utf8')) if os.path.exists(ip) else {}
    for sl in slugs:
        dos, gem = DOSSIER[sl], []
        for g, cfg in G.items():
            mo = moties(g, cfg, dos)
            rg = R.get(sl, {}).get(cfg['cvdr'], [])
            gem.append(dict(naam=cfg['naam'], ris=cfg.get('ris_url', ''), sinds=SINDS[:4], n_moties=sum(1 for m in mo if not m.get('tekst')), moties=mo, regels=rg,
                            uitslag=cfg.get('uitslag_tekst'), n_uitslag=sum(1 for m in mo if m['uitslag'])))
            print(sl, g, len(mo), 'moties', len(rg), 'regels', file=sys.stderr, flush=True)
        uit = dict(slug=sl, stand_ori=min(v for v in so.values() if v), stand_cvdr=B.get('stand_cvdr', ''), gemeenten=gem)
        json.dump(uit, open(os.path.join(uitmap, sl + '.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
        index[sl] = len(gem)
    json.dump(index, open(ip, 'w', encoding='utf8'), ensure_ascii=False)


if __name__ == '__main__':
    main(sys.argv[1:])
