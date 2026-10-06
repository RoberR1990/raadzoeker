# Raadzoeker

Wat de Rotterdamse raad zegt, besluit en belooft, op één plek: **https://raadzoeker.nl**

- Elke vergadering samengevat (kort en uitgebreid, met letterlijke citaten en het videomoment)
- Zoeken in alles wat raad, commissies en wijkraden sinds 2018 zeiden en schreven
- Een pagina per domein, onderwerp en gebied
- Onderwerpen volgen, met meldingen als je wilt

## Mappen

- `docs/` — de site (statisch, Cloudflare Pages), met de data in `docs/data/` en `docs/ontwerp/`
- `functions/` — kleine serverfuncties (anonieme zoekteller, fout melden, meldingen)
- `src/` — pijplijn: ophalen, verwerken, controleren
- `data/` — samenvattingen
- `nas/` — automatische bijwerker
- `video/` — promovideo (Remotion)

Zie `CLAUDE.md` voor opbouw, dataformaat, beperkingen en volgende stappen.

## Open data en privacy

Alle informatie komt uit openbare bronnen: iBabs van de gemeenteraad en de wijkraden van Rotterdam, de openbare video en ondertiteling van de vergaderingen, officielebekendmakingen.nl, CBS, PDOK, RDW Open Data, Rekenkamer Rotterdam en Ombudsman Rotterdam-Rijnmond. Geen accounts, geen tracking, geen opgeslagen IP-adressen; namen van insprekers en bewoners worden niet getoond. Zie https://raadzoeker.nl/ontwerp/over.html#privacy.

Onofficieel hulpmiddel van Robert Riteco; geen product van de gemeente Rotterdam of de griffie.

## Licentie

De code valt onder de [EUPL-1.2](LICENSE). De brondata blijven onder de voorwaarden van de oorspronkelijke bronnen.
