# Raadzoeker — overdracht

Zoektool voor wat er in de Rotterdamse gemeenteraad en raadscommissies is gezegd. Eigenaar: Robert Riteco. Taal met Robert: Nederlands, kort, gewone taal, gefaseerd opleveren, bij een blokkade stoppen en voorleggen. Zwaar uitvoerend werk (samenvatten) naar lichte modellen/subagents.

## Mappen

- `docs/` — de site (GitHub Pages, map `/docs` op `main`). `index.html` is de startpagina; `raadzoeker.html` en `commissiezoeker-*.html` zijn op zichzelf staande bestanden met alle data erin.
- `src/` — pijplijn en app. Alle paden staan in `src/paden.py` (overschrijfbaar met env `RZ_BRON`, `RZ_WERK`, `RZ_STAND`). `src/oud/` = losse patches die al in `template.html` zitten (niet opnieuw toepassen).
- `data/raad/`, `data/commissies/` — per jaar `JAAR.zst` (JSON, zstd niveau 22) plus `meta*.json`. Dit is de invoer voor `assemble.py`.
- `data/sum/` — AI-samenvattingen per debat, 2026 (Sonnet-subagents). `index.json` koppelt id aan (datum, agendapunt); afgeleid uit de gebouwde data omdat de oorspronkelijke invoerbestanden weg zijn (122 van 137 gekoppeld, net als voorheen).
- `data/tsum/` — AI-samenvattingen per thema. 27 van 41 klaar (id = index in de platte themalijst uit `themes.py`). Ontbreken: 24–26 en 30–40. Nog niet ingebouwd in de app. `INSTRUCTIES.md` is de opdracht voor de subagent; de invoerbestanden (`in_NN.txt`) staan niet in git en moeten opnieuw uit de data worden gemaakt.

## Niet in git (te groot), wel op Roberts pc in `D:\Downloads Chrome`

- `raadzoeker-bundle (1).dat` (335 MB): agenda-html en notulen-pdf's raad 2018–2026. Formaat: 8 bytes `RZBUNDL1`, uint32 LE headerlengte, JSON-header `{meetings, docs, files:[{name,size}]}`, dan de bestanden achter elkaar.
- `raadzoeker-ondertitels.json.gz`, `raadzoeker-ondertitels-2.json.gz`: ondertitels raad.
- `raadzoeker-commissies-meta.json.gz`, `raadzoeker-commissies-subs-c.json.gz`, `raadzoeker-commissies-subs-i.json.gz`: commissies.

## Bouwen

Vanuit de repo-root, Python 3.12 met `pymupdf beautifulsoup4 lxml numpy zstandard`, en eenmalig `npm install` in `src/js`:

- `python src/maak.py` — alleen de site: `data/` → `docs/*.html` (geen bronbestanden nodig, ca. 1 min).
- `python src/maak.py alles` — volledige pijplijn uit de bronbestanden → `data/` → `docs/` (ca. 10 min). Ook `raad` of `commissies` los.
- Tussenbestanden (ca. 1 GB) in de werkmap `D:\Downloads Chrome\raadzoeker-werk` (C: is vol). `bron.py` pakt daar de bundle uit en zet ondertitels/commissiemeta klaar.
- Getest 2-10-2026: herbouw uit de bronnen geeft byte-identieke `data/` en `docs/`, op één teller na (`tot.sp` telt nu ook ondertitelde spreekbeurten, zoals de code doet).
- `maak.py` zet `PYTHONUTF8=1`; zonder dat leest Windows de json als cp1252 en krijg je kapotte namen.

## Pijplijn (raad)

`extract.py` (pdf → regels, PyMuPDF) → `agenda.py` (agenda-html → `agendas.json`) → `parse.py` (sprekers, agendapunten → `segs.json`) → `build.py` (sprekerregister, partijen, moties als eigen blok) → `emit.py` (per jaar JSON + zst, ondertitels uitlijnen, moties, toezeggingen, samenvattingen) → `insights.py` (thema's en inzichten in `meta.json`) → `assemble.py <uit.html>` (data + `template.html` → één bestand).

Commissies: `emit_comm.py` → `insights.py` → `assemble.py`, met env `RZ_OUT=outc`, `RZ_YEARS=2022,2023`, `RZ_META=outc/meta_2022-2023.json`. `variant.py` zet teksten om naar de Commissiezoeker.

Hulpmodules: `subs.py` (ondertitels uitlijnen), `motions.py` (stemuitslag), `toez.py` (toezeggingen op formulering), `themes.py` (41 thema's in 3 groepen, met subthema's). `harvest.js` haalde data op via de browser. `test*.py` zijn Playwright-tests.

## Dataformaat per jaar

`M` vergaderingen `[datum, agendaId, label, hasN (1 notulen / 2 ondertitels / 0 alleen tijdlijn), vref]`; `I` agendapunten `[mIdx, nr, titel]`; `D` documenten; `s` kolommen `m,i,k,sp,pa,ro,pg,d,z,t,v`; `mo` moties; `tz` toezeggingen; `sm` samenvattingen. Soort `k`: 0 spreekbeurt, 1 motie/stemming, 2 presentielijst, 3 alleen tijdlijn, 4 automatische ondertiteling. In de html staat de data als base91-paren (13 bits per 2 tekens) in `<script type="application/octet-stream" id="dJAAR">`, uitgepakt met fzstd.

## Bronnen

- Raad: `gemeenteraad.rotterdam.nl` (iBabs). Vergadering: `/Agenda/Index/{agendaId}`. Lijsten: `/Agenda/RetrieveAgendasForYear?agendatypeId={id}&year={j}` (raad = 100002367).
- Video: Company Webcast (`sdk.companywebcast.com`, `seek({timestamp})`) en voor 2023–2024 Connect Live (`connectlive.ibabs.eu/Player/Player/{agendaId}`).
- Wijkraden: `wijkraad.rotterdam.nl` (39 raden, besluitenlijsten als pdf, geen video). Nog niet opgehaald.

## Bekende beperkingen

- Toezeggingen zijn herkend op formulering, geen officiële griffielijst.
- Agendapunt kan soms verkeerd gekoppeld zijn.
- Thema "Noord" vangt ook Diergaarde Blijdorp.
- AI-samenvattingen zijn alleen steekproefsgewijs gecontroleerd.
- Stemgedrag: betrouwbaar voor patronen per fractie, niet per raadslid.
- Sprong naar het juiste videomoment bij Connect Live is niet geverifieerd.

## Volgende stappen (afgesproken volgorde)

1. ~~Paden in `src/` aanpassen aan deze mappenindeling; build herhaalbaar maken.~~ Klaar 2-10-2026.
2. Data per jaar als los bestand laten laden (nu 20 MB vooraf); commissies weer één tool.
3. Ontbrekende 14 themasamenvattingen maken en tonen (gelabeld als AI).
4. Raadsstukken en de griffielijst van toezeggingen/moties uit iBabs.
5. Rekenkamer Rotterdam en ombudsman.
6. Wijkraden.
