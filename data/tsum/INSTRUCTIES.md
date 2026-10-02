# Opdracht: themasamenvattingen gemeenteraad Rotterdam

Je maakt per thema een korte samenvatting van wat er in de gemeenteraad van Rotterdam (2018–2026) over dat thema is gezegd, voor een zoektool voor ambtenaren.

Het invoerbestand bevat meerdere thema's. Elk thema begint met `### THEMA id=<nummer> | groep: ... | naam: ...`, daarna de zoektermen, de trend per jaar, en per jaar een selectie fragmenten uit spreekbeurten in de vorm `[datum | agendapunt] Naam (partij, rol): fragment`.
Let op: het zijn fragmenten rond een zoekterm, geen hele debatten, en een selectie, niet alles.

Lees het hele invoerbestand met de Read-tool (in delen met offset/limit als het lang is; lees ALLES voordat je schrijft).

Schrijf daarna met de Write-tool het uitvoerbestand met geldige JSON: een lijst met per thema één object:
{"id": <nummer als getal>,
 "kern": "<3 tot 4 zinnen: waar gaat het in de raad bij dit thema vooral over, wat zijn de terugkerende kwesties>",
 "ontwikkeling": [{"periode": "<jaar of jaren, bv. 2019–2020>", "wat": "<één zin: wat speelde er toen>", "citaat": "<letterlijk stuk van 6 tot 25 woorden uit één fragment uit die periode dat dit onderbouwt>"}],
 "standpunten": [{"wie": "<fractienaam of naam + rol collegelid>", "punt": "<één zin: de lijn van deze fractie/dit collegelid op dit thema, zoals die uit de fragmenten blijkt>", "citaat": "<letterlijk stuk van 6 tot 25 woorden uit een fragment van díe fractie/persoon dat dit onderbouwt>"}],
 "recent": "<1 tot 2 zinnen over wat er in 2025–2026 speelt, of lege string als er geen recente fragmenten zijn>"}

Regels:
- Nederlands, neutraal en zakelijk, gewone taal, geen jargon, geen oordeel.
- Gebruik ALLEEN wat in de fragmenten staat. Verzin niets en vul niets aan uit eigen kennis. Bij twijfel weglaten.
- "ontwikkeling": 3 tot 5 regels, chronologisch. "standpunten": maximaal 6, per fractie hooguit één, alleen als het standpunt in meerdere fragmenten of heel duidelijk terugkomt.
- Wees voorzichtig met algemene uitspraken: schrijf "in de fragmenten" of "meermaals" in plaats van "altijd". Noem geen cijfers tenzij ze letterlijk in een fragment staan.
- Bij wijken en gebieden: beschrijf welke onderwerpen over die wijk in de raad terugkomen.
- Sommige fragmenten zijn automatische ondertiteling (2026) en bevatten herkenningsfouten: wees terughoudend met namen en cijfers daaruit.
- Elk thema uit het bestand precies één keer, met het juiste id.
- "citaat" moet tekens-voor-teken gekopieerd zijn uit het invoerbestand (zelfde woorden, zelfde volgorde, zelfde leestekens), zonder de naam ervoor of de … erachter. Beweringen waarvan het citaat niet letterlijk in de bron staat, worden na afloop automatisch geschrapt (`src/tsum_check.py`). Kun je geen citaat vinden, laat de bewering dan weg.
- Lees GEEN andere bestanden dan het invoerbestand (ook geen eerdere uitvoer als voorbeeld): elke naam, straat, wijk en fractie moet letterlijk in de fragmenten van dít thema staan.
- Een fractie bij "standpunten" alleen als minstens twee fragmenten van die fractie het standpunt dragen. Geen beweringen over groei of afname tenzij de trendcijfers dat laten zien.

Antwoord na het schrijven alleen met het aantal thema's en het pad van het uitvoerbestand.
