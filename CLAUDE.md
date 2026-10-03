# Raadzoeker — overdracht

Zoektool voor wat er in de Rotterdamse gemeenteraad en raadscommissies is gezegd. Eigenaar: Robert Riteco. Taal met Robert: Nederlands, kort, gewone taal, gefaseerd opleveren, bij een blokkade stoppen en voorleggen. Zwaar uitvoerend werk (samenvatten) naar lichte modellen/subagents.

## Mappen

- `docs/` — de site, https://raadzoeker.pages.dev (achter Cloudflare Access). Hosting: Cloudflare Pages, gekoppeld aan deze repo (branch `main`, uitvoermap `docs`, geen build-commando), afgeschermd met Cloudflare Access (alleen toegelaten e-mailadressen). Elke push naar `main` zet de site vanzelf opnieuw online. Limiet: 25 MB per bestand (grootste jaarbestand nu 7,7 MB). `_headers` vraagt zoekmachines niet te indexeren. `index.html` is de startpagina; `raadzoeker.html` en `commissiezoeker.html` (2022–2026) zijn kleine pagina's (0,13 MB) die de jaardata uit `docs/data/raad/` en `docs/data/commissies/` ophalen (`JAAR.zst` = JSON, zstd niveau 22, plus `meta.json`; alle downloads starten tegelijk, verwerken nieuwste jaar eerst). `commissiezoeker-2022-2023/2024-2025/2026.html` zijn alleen nog doorverwijzingen.
- `src/` — pijplijn en app. Alle paden staan in `src/paden.py` (overschrijfbaar met env `RZ_BRON`, `RZ_WERK`, `RZ_STAND`). `src/oud/` = losse patches die al in `template.html` zitten (niet opnieuw toepassen).
- `data/sum/` — AI-samenvattingen per debat, 2026 (Sonnet-subagents). `index.json` koppelt id aan (datum, agendapunt); afgeleid uit de gebouwde data omdat de oorspronkelijke invoerbestanden weg zijn (122 van 137 gekoppeld, net als voorheen).
- `data/tsum/` — AI-samenvattingen per thema (id = index in de platte themalijst uit `themes.py`). In de Raadzoeker zichtbaar boven de resultaten als je een thema kiest, gelabeld als AI. 0–23 en 27–29 eerder gemaakt (zonder citaten). 24, 26 en 30–40 op 3-10-2026 met Haiku, elk één thema per agent, mét een letterlijk citaat per ontwikkeling/standpunt; `src/tsum_check.py --schrijf` schrapt alles waarvan het citaat niet woordelijk (en bij standpunten: in een fragment van die fractie) in de bron staat, en de app toont het citaat. Thema 25 (Toezeggingen) bewust zonder samenvatting: Haiku schreef uitspraken van wethouders toe aan fracties, en de officiële toezeggingenlijst (stap 4) is beter. Invoer maken: `python src/tsum_in.py 24 t24`.

## Niet in git (te groot), wel op Roberts pc in `D:\Downloads Chrome`

- `raadzoeker-bundle (1).dat` (335 MB): agenda-html en notulen-pdf's raad 2018–2026. Formaat: 8 bytes `RZBUNDL1`, uint32 LE headerlengte, JSON-header `{meetings, docs, files:[{name,size}]}`, dan de bestanden achter elkaar.
- `raadzoeker-ondertitels.json.gz`, `raadzoeker-ondertitels-2.json.gz`: ondertitels raad.
- `raadzoeker-commissies-meta.json.gz`, `raadzoeker-commissies-subs-c.json.gz`, `raadzoeker-commissies-subs-i.json.gz`: commissies.

## Bouwen

Vanuit de repo-root, Python 3.12 met `pymupdf beautifulsoup4 lxml numpy zstandard`, en eenmalig `npm install` in `src/js`:

- `python src/maak.py` — alleen de pagina's: `docs/data/` → `docs/*.html` (geen bronbestanden nodig, enkele seconden).
- `python src/maak.py alles` — volledige pijplijn uit de bronbestanden → `docs/data/` → `docs/*.html` (ca. 10 min). Ook `raad` of `commissies` los.
- Tussenbestanden (ca. 1 GB) in de werkmap `D:\Downloads Chrome\raadzoeker-werk` (C: is vol). `bron.py` pakt daar de bundle uit en zet ondertitels/commissiemeta klaar.
- Getest 2-10-2026: herbouw uit de bronnen geeft byte-identieke `data/` en `docs/`, op één teller na (`tot.sp` telt nu ook ondertitelde spreekbeurten, zoals de code doet).
- Lokaal bekijken/testen: `python -m http.server 8765 -d docs` (via `file://` werkt het ophalen niet). Gemeten 2-10-2026 lokaal: raad 1,4 s en ca. 280 MB geheugen, commissies 2,8 s en ca. 550 MB. Dat laatste is zwaar voor telefoons.
- `maak.py` zet `PYTHONUTF8=1`; zonder dat leest Windows de json als cp1252 en krijg je kapotte namen.

## Pijplijn (raad)

`extract.py` (pdf → regels, PyMuPDF) → `agenda.py` (agenda-html → `agendas.json`) → `parse.py` (sprekers, agendapunten → `segs.json`) → `build.py` (sprekerregister, partijen, moties als eigen blok) → `emit.py` (per jaar JSON + zst, ondertitels uitlijnen, moties, toezeggingen, samenvattingen) → `insights.py` (thema's en inzichten in `meta.json`) → `assemble.py <uit.html>` (data + `template.html` → één bestand).

Commissies: `emit_comm.py` → `insights.py` → `assemble.py`, met env `RZ_OUT=outc` (alle jaren samen). `variant.py` zet teksten om naar de Commissiezoeker.

Hulpmodules: `subs.py` (ondertitels uitlijnen), `motions.py` (stemuitslag), `toez.py` (toezeggingen op formulering), `themes.py` (41 thema's in 3 groepen, met subthema's). `harvest.js` haalde data op via de browser. `test*.py` zijn Playwright-tests.

## Dataformaat per jaar

`M` vergaderingen `[datum, agendaId, label, hasN (1 notulen / 2 ondertitels / 0 alleen tijdlijn), vref]`; `I` agendapunten `[mIdx, nr, titel]`; `D` documenten; `s` kolommen `m,i,k,sp,pa,ro,pg,d,z,t,v`; `mo` moties; `tz` toezeggingen; `sm` samenvattingen. Soort `k`: 0 spreekbeurt, 1 motie/stemming, 2 presentielijst, 3 alleen tijdlijn, 4 automatische ondertiteling. De pagina haalt `META.dir + JAAR.zst?v=hash` op en pakt uit met fzstd (in de pagina ingebouwd).

## Bronnen

- Raad: `gemeenteraad.rotterdam.nl` (iBabs). Vergadering: `/Agenda/Index/{agendaId}`. Lijsten: `/Agenda/RetrieveAgendasForYear?agendatypeId={id}&year={j}` (raad = 100002367).
- Video: Company Webcast (`sdk.companywebcast.com`, `seek({timestamp})`) en voor 2023–2024 Connect Live (`connectlive.ibabs.eu/Player/Player/{agendaId}`).
- Wijkraden: `wijkraad.rotterdam.nl` is ook iBabs. `wijkraden.py` haalt 4 rapportages op (ongevraagde adviezen 41, wijkakkoorden en -plannen 39, collegereacties op wijkplannen 39, wijkverslagen 154) met detail en pdf-tekst; de gevraagde wijkraadadviezen (783 sinds 2022) staan in de raads-iBabs (`ibabs_items.py wijkraadadviezen`). Alles in tabblad Officiële stukken; de themabalk heeft een link 'Officiële stukken bij dit thema' (zelfde zoektermen, dus bij een wijkthema ook de wijkraadstukken). Vergaderingen/besluitenlijsten van de wijkraden zelf nog niet opgehaald. `ibabs.py` heeft één gedeelde limiet voor alle iBabs-hosts, ook over processen heen (`.slot`/`.laatste` in de werkmap).
- Officiële stukken (iBabs-rapportages, `/Reports/Details/{id}`, data via POST `/Reports/GetReportData/{id}`, max 100 rijen per keer; detail `/Reports/Item/{id}`; pdf via `/Document/View/{documentId}`). Scripts: `ibabs.py` (ophaler, 1 verzoek/sec, cache in werkmap, stopt bij 403/429/captcha), `ibabs_lijsten.py` (alle lijsten), `ibabs_items.py <soorten>` (details + motietekst, hervatbaar), `ibabs_emit.py` → `docs/data/ibabs/stukken.zst`, tabblad "Officiële stukken". Vanaf 2018: 6.556 toezeggingen, 6.842 moties, 260 amendementen, 67 initiatiefvoorstellen, 802 raadsvoorstellen (vanaf 2022 in iBabs), 950 collegebesluiten, 10.522 collegebrieven, 4.425 schriftelijke vragen. Details en motieteksten alleen voor toezeggingen, moties, amendementen, initiatief- en raadsvoorstellen; brieven/vragen/besluiten alleen lijst + link.
- Koppeling notulen ↔ iBabs: `ibabs_emit.py` koppelt de moties/amendementen uit de notulen (veld `mo`) op datum (±3 dagen) en titel aan iBabs → `docs/data/ibabs/moties.json`; 5.882 van 6.297 (93%), steekproef 20/20 juist. In Moties & stemmingen staat dan 'officiële tekst en afdoening →'.
- Rekenkamer Rotterdam (`rekenkamer.rotterdam.nl/onderzoeken`, 67 Rotterdamse onderzoeken vanaf 2017) en Ombudsman Rotterdam-Rijnmond (`orr.nl`, WordPress-API, 53 rapporten/jaarverslagen/brieven die Rotterdam noemen): `extern.py`, opgenomen in hetzelfde tabblad. "Besproken" = raadsvergaderingen waarin de rapporttitel letterlijk binnen 400 tekens van "rekenkamer"/"ombudsman" valt, na publicatie (26 van 67 rekenkamerrapporten; ombudsmanrapporten worden zo nooit gevonden).

## Bekende beperkingen

- Toezeggingen zijn herkend op formulering, geen officiële griffielijst.
- Agendapunt kan soms verkeerd gekoppeld zijn.
- Thema "Noord" vangt ook Diergaarde Blijdorp.
- AI-samenvattingen zijn alleen steekproefsgewijs gecontroleerd. Les uit 3-10-2026: Haiku-samenvattingen zónder citaten bevatten overgenomen namen uit voorbeeldbestanden en partijclichés, en Haiku als controleur keurt vrijwel alles goed met deels verzonnen citaten. Alleen de mechanische citaatcontrole is betrouwbaar; die vangt verzonnen citaten, niet een te ruime samenvatting van een echt citaat. De `kern`-zinnen hebben geen citaat en zijn dus het minst gecontroleerd.
- Stemgedrag: betrouwbaar voor patronen per fractie, niet per raadslid.
- Sprong naar het juiste videomoment bij Connect Live is niet geverifieerd.

## Redesign (besloten 3-10-2026, nog niet gebouwd)

Doel: van citatenzoeker naar een site die laat zien wat er in de stad speelt, voor iedereen, modulair; eerst gericht op gemeenteambtenaren via intranet, met een hoog wow-gehalte zodat hij zich verspreidt. Site blijft voorlopig achter Cloudflare Access; de regel gaat naar alle @rotterdam.nl-adressen (akkoord Robert, instellen in Cloudflare). Geen functies die een AI-sleutel nodig hebben. Automatisch (wekelijks) bijwerken mag via de NAS.

Gekozen modules voor het eerste prototype:
1. **Raad Wrapped**: jaar/raadsperiode in deelbare kaarten (woord van het jaar, meest besproken wijk, opkomende onderwerpen, enz.); lanceercampagne.
2. **Mijn dossier**: kies onderwerp/afdeling → wat de raad zei, open moties en toezeggingen met deadlines, welke fracties ermee bezig zijn.
3. **Briefing-generator**: A4/pdf per onderwerp met eerdere moties, toezeggingen, standpunten (met citaten) en rekenkamerbevindingen.
5. **Levende stadskaart** als binnenkomer: wijken kleuren naar aandacht, tijdschuif 2018–2026.

Ontwerpschermen (3-10-2026) in `docs/ontwerp/`: `startpagina.html` (dossier voorop, kaart, beloftemonitor, Wrapped), `dossier.html`, `briefing.html` (printbaar A4), gedeelde `stijl.css`. Huisstijl gemeente Rotterdam (onzestijl.rotterdam.nl): groen #00811F + wit, tekst zwart, contrastgrijs #EFF4F6, lettertype Bolder als dat lokaal staat, anders Arial (Bolder is van de gemeente; niet meeleveren), geen kapitalen, links onderstreept, citaten met enkele aanhalingstekens. Niet als artifact publiceren (officiële huisstijl op onofficieel hulpmiddel); alleen op de eigen afgeschermde site. Data: `src/ontwerp_data.py` → `dossiers.json` (41 thema's; stukken horen bij een thema als het zoekwoord in de titel staat of minstens 3× in de tekst), `src/kaart.py` → `kaart.json` (CBS wijken 2024 via PDOK WFS `wijkenbuurten:wijken`, gemeentecode GM0599, EPSG:4326; de 14 CBS-wijken komen overeen met de gebieden), `start.json` (stadspols, Wrapped). Volgorde volgens Robert: dossier eerst (ambtenaren denken in dossiers), kaart secundair.

Ook hoog en haalbaar (eerder genoemd): Mijn wijk, Dossiers, Beloftemonitor, Wie is wie, Stadspols. Later: organisatiepagina's, volgen/alerts, tijdmachine, partijvergelijker, verbanden. Ontwerpregels: binnen 1 s iets zien (kleine voorberekende bestanden per pagina, geen 20 MB), antwoord eerst en bron één klik dieper, deelbare links met voorvertoning, goed op mobiel, onofficieel maar verzorgd. Plaatsing op intranet via Communicatie als pilot; privacycheck.

## Volgende stappen (afgesproken volgorde)

1. ~~Paden in `src/` aanpassen aan deze mappenindeling; build herhaalbaar maken.~~ Klaar 2-10-2026.
2. ~~Data per jaar als los bestand laten laden (nu 20 MB vooraf); commissies weer één tool.~~ Klaar 2-10-2026.
3. ~~Ontbrekende 14 themasamenvattingen maken en tonen (gelabeld als AI).~~ Klaar 2-10-2026.
4. ~~Raadsstukken en de griffielijst van toezeggingen/moties uit iBabs.~~ Klaar 3-10-2026 (alle details opgehaald; stand 02-10-2026).
5. ~~Rekenkamer Rotterdam en ombudsman.~~ Klaar 3-10-2026.
6. ~~Wijkraden: adviezen, reacties college, wijkakkoorden.~~ Klaar 3-10-2026 (zonder vergaderverslagen van de wijkraden zelf).
7. Officiële bekendmakingen (Gemeenteblad, verordeningen; open API): wat er na het debat is vastgesteld.
8. CBS-wijkcijfers en Wijkprofiel Rotterdam naast de wijkthema's.
9. Open Raadsinformatie (VNG/Open State): zelfde soort data voor andere gemeenten, route naar G4.
10. Tweede Kamer open data: landelijk debat over hetzelfde dossier.
11. MRDH en Provinciale Staten Zuid-Holland: regionale besluiten OV en wonen.

Niet doen: lokale media (Rijnmond, AD) overnemen, auteursrecht; hooguit linken. Afgesproken 2-10-2026.
