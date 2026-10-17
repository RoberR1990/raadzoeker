"""Maakt src/elders_bron.json uit de fase-0-uitkomsten (moties_regels.json, cvdr_regels.json)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(H, 'moties_regels.json'), encoding='utf8'))
pc = os.path.join(H, 'cvdr_regels.json')
C = json.load(open(pc, encoding='utf8')) if os.path.exists(pc) else {}
NAAM = {'amsterdam': ('Amsterdam', 'Amsterdam'), 'den_haag': ('Den Haag', "'s-Gravenhage"), 'utrecht': ('Utrecht', 'Utrecht'),
        'eindhoven': ('Eindhoven', 'Eindhoven'), 'dordrecht': ('Dordrecht', 'Dordrecht'), 'vlaardingen': ('Vlaardingen', 'Vlaardingen')}
VELD = ['motie_rx', 'amendement_rx', 'titel_rx', 'uitsluit_rx', 'ori_query', 'uitslag_naam_rx']
G = {}
for g, (nm, cv) in NAAM.items():
    r = M[g]
    G[g] = dict(naam=nm, cvdr=cv, ris_url=r.get('ris', ''), **{k: r[k] for k in VELD if k in r})
G['utrecht'].update(geen_moties=True, uitslag_tekst='Utrecht zet losse moties niet in Open Raadsinformatie, alleen lijsten van aangenomen moties. Zie de raadsinformatie van Utrecht.')
G['dordrecht']['uitslag_tekst'] = None
uit = dict(stand_cvdr=C.pop('_stand', '2026-10-17') if C else '', gemeenten=G, regels=C)
json.dump(uit, open(os.path.join(H, '..', '..', 'src', 'elders_bron.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('gemeenten', len(G), 'regels', {k: sum(len(v) for v in d.values()) for k, d in C.items()})
