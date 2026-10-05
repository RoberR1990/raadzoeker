Je vat het Rotterdamse coalitieakkoord 2026-2030 'Vaart maken' samen voor gemeenteambtenaren, op basis van ALLEEN de tekst in {IN}. Lees het hele bestand. Elke pagina heeft een code A<paginanummer>.

Doel: snel snappen wat dit college van plan is: de grote lijnen (de 'doorbraken' en het 'fundament'), wat het per beleidsdomein betekent, en de financiële keuzes. Dit akkoord zet de toon voor de komende jaren.

Regels (streng):
- Elke zin/elk punt heeft precies één broncode (de pagina, bijvoorbeeld A42) en een LETTERLIJK citaat van die pagina: 8 tot 30 woorden, exact gekopieerd (ook hoofdletters en leestekens mogen afwijken, woorden niet), zonder iets weg te laten. Een script controleert dit woord voor woord en schrapt alles wat niet klopt.
- Beschrijf alleen wat het akkoord zegt, als voornemen van de coalitie ("De coalitie wil …", "Het akkoord noemt …"). Geen eigen oordeel, geen woorden als "ambitieus" of "helaas". Neutraal, gewone taal (B1), korte zinnen.
- Liever minder punten die kloppen dan veel punten.

Een "zin" is steeds: {"zin": "…", "bron": "A12", "citaat": "…"}. Een "punt" is: {"wat": "korte zin, max 20 woorden", "bron": "A12", "citaat": "…"}.

Schrijf het resultaat als JSON (UTF-8, geen markdown eromheen) naar {UIT}:
{
 "partijen": ["PRO", "D66", "VVD", "CDA", "Volt"],   // zoals in het akkoord
 "kern": [zin, …],                   // 5-7 zinnen: de kern van het akkoord
 "hoofdstukken": [                   // de drie doorbraken, het fundament, financiën en lokale democratie; per onderdeel
   {"titel": "Doorbraak 1: Een huis voor iedereen", "intro": [zin, zin], "punten": [punt, …]}   // 4-8 punten per onderdeel
 ],
 "domeinen": {                       // per beleidsdomein van de site 2-6 punten; laat een domein weg als het akkoord er niets over zegt
   "wonen": [punt], "buitenruimte": [punt], "mobiliteit": [punt], "economie": [punt], "klimaat": [punt], "veiligheid": [punt], "zorg": [punt],
   "onderwijs": [punt], "werk": [punt], "samenleven": [punt], "cultuur": [punt], "bestuur": [punt], "financien": [punt]
 },
 "geld": [punt, …]                    // 3-6 punten over investeringen, bezuinigingen en lokale lasten
}
Codes van de domeinen: wonen = wonen en bouwen; buitenruimte = openbare ruimte, groen, afval; mobiliteit = verkeer, parkeren, OV; economie = economie en haven; klimaat = klimaat en energie; veiligheid = veiligheid en handhaving; zorg = zorg, welzijn en jeugd; onderwijs; werk = werk, inkomen en armoede; samenleven = samenleven en participatie; cultuur = cultuur en sport; bestuur = bestuur en organisatie; financien.

Meld na afloop in maximaal 2 regels: aantal punten per onderdeel.
