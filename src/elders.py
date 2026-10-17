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


def moties(g, cfg, dos):
    idx = f"ori_{g}_2*"
    body = {'size': MAX, '_source': ['name', 'last_discussed_at', 'original_url', 'text'],
            'sort': [{'last_discussed_at': 'desc'}],
            'query': {'bool': {'must': [{'term': {'@type': 'MediaObject'}}, cfg['ori_query'],
                                        {'query_string': {'query': dos['q'], 'fields': ['name', 'text']}},
                                        {'range': {'last_discussed_at': {'gte': SINDS}}}]}}}
    h = ori(idx, body)['hits']['hits']
    mrx, arx = re.compile(cfg['motie_rx'], re.I), re.compile(cfg.get('amendement_rx') or r'(?!x)x', re.I)
    urx = re.compile(cfg['uitsluit_rx'], re.I) if cfg.get('uitsluit_rx') else None
    trx = re.compile(cfg['titel_rx'], re.I) if cfg.get('titel_rx') else None
    orx = re.compile(dos['rx'])
    uit, gezien = [], set()
    for x in h:
        s = x['_source']; naam = (s.get('name') or '').strip()
        soort = 'amendement' if arx.search(naam) else 'motie' if mrx.search(naam) else None
        if not soort or (urx and urx.search(naam)):
            continue
        if not (orx.search(naam.lower()) or len(orx.findall(tekst(s).lower())) >= 2):
            continue
        titel, ind = naam, ''
        m = trx.search(naam) if trx else None
        if m:
            gd = m.groupdict()
            titel = (gd.get('titel') or naam).strip(' -–.')
            ind = (gd.get('indieners') or '').strip(' -–.()')
        titel = re.sub(r'\.(pdf|docx?)$', '', titel, flags=re.I)
        k = (titel.lower(), (s.get('last_discussed_at') or '')[:10])
        if k in gezien:
            continue
        gezien.add(k)
        uit.append(dict(datum=(s.get('last_discussed_at') or '')[:10], soort=soort, titel=titel, indieners=ind, url=s.get('original_url') or ''))
    return uit


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
            gem.append(dict(naam=cfg['naam'], ris=cfg.get('ris_url', ''), sinds=SINDS[:4], n_moties=len(mo), moties=mo, regels=rg,
                            uitslag=cfg.get('uitslag_tekst')))
            print(sl, g, len(mo), 'moties', len(rg), 'regels', file=sys.stderr, flush=True)
        uit = dict(slug=sl, stand_ori=min(v for v in so.values() if v), stand_cvdr=B.get('stand_cvdr', ''), gemeenten=gem)
        json.dump(uit, open(os.path.join(uitmap, sl + '.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
        index[sl] = sum(1 for x in gem if x['moties'] or x['regels'])
    json.dump(index, open(ip, 'w', encoding='utf8'), ensure_ascii=False)


if __name__ == '__main__':
    main(sys.argv[1:])
