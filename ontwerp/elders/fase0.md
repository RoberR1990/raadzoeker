# Elders: fase 0, datacheck (17-10-2026)

## Strategie (besloten 16-10-2026)

- Richting: vergelijken, niet verbreden. Geen Raadzoeker per gemeente. In Rotterdamse dossiers komt een laag "Elders": wat andere gemeenten over hetzelfde onderwerp besloten en vastgelegd hebben.
- Waarom: zoeken in raadsinformatie bestaat al (ORI/openbesluitvorming.nl, MAAT van AethiQs bij ~10 gemeenten, eigen zoeken van Notubiz en iBabs). Wat Raadzoeker sterk maakt (dossiers, Beloofd, keten, gecontroleerde Opus-samenvattingen) groeit niet mee: één Opus-onderwerp kost 350-700k tokens. Rotterdamse collega's hebben meer aan "hoe doen anderen het?" dan aan een Haagse zoeker.
- Later uitbreiden blijft mogelijk (besluit Robert: "in de toekomst misschien wel"). Daarom krijgt de data vanaf het begin een veld `gemeente`.
- Fase 1: Parkeren, Handhaving en toezicht, Deelscooters. Zonder AI, neutraal naast elkaar, geen ranglijst. Gebruik meten met Umami; dat is de drempel voor fase 2.

## Wat is gecheckt

Script `ontwerp/elders/check.py`, uitkomst in `check.json`. Bewust buiten `src/`, zodat het niet onder het codeslot valt.

- Bronnen: Open Raadsinformatie (Elasticsearch op `api.openraadsinformatie.nl/v1/elastic/`, 331 indexen) en CVDR (SRU `zoekservice.overheid.nl`, `x-connection=cvdr`).
- Gemeenten: G4, plus Eindhoven, Tilburg, Groningen, Schiedam, Dordrecht en Vlaardingen. Rotterdam dient als controle tegen onze eigen data.

## Uitkomst per gemeente

Telling vanaf 2022. "moties X" = document met 'motie' in de naam en het onderwerp in naam of tekst; bijlagen en motielijsten tellen mee.

| gemeente | RIS | laatste vergadering in ORI | motie in naam | moties parkeren | deelvervoer | handhaving | CVDR parkeerbel. / APV nieuwste |
|---|---|---|---|---|---|---|---|
| Rotterdam (controle) | iBabs | 10-07-2026 | 3.471 | 34 | 34 | 47 | 2026-01 / 2026 |
| Amsterdam | Notubiz | 02-07-2026 | 7.645 | 143 | 113 | 58 | 2024-07 (parkeerverord. 2026-07) / 2026-10 |
| Den Haag | Notubiz | 09-07-2026 | 7.439 | 228 | 119 | 106 | 2026-01 / 2026-10 |
| Utrecht | iBabs | 02-07-2026 | 57 | 2 | 2 | 2 | 2026-01 / 2026-11 |
| Eindhoven | Notubiz | 08-07-2026 | 601 | 14 | 6 | 7 | 2025-12 / 2026-07 |
| Tilburg | ? | 07-07-2026 | 794 | 8 | 2 | 9 | 2025-12 / 2027-01 |
| Groningen | eigen API | 01-07-2026 | 57 | 5 | 1 | 1 | 2025-11 / 2026-09 |
| Schiedam | ? | 08-07-2026 | 222 | 0 | 1 | 1 | 2026-05 / 2026-09 |
| Dordrecht | ? | 07-07-2026 | 1.020 | 2 | 2 | 7 | 2026-01 / 2026-10 |
| Vlaardingen | ? | 09-07-2026 | 764 | 11 | 4 | 9 | 2026-01 / 2026-10 |

RIS is afgeleid uit `original_url`; "?" = niet nagekeken.

## Bevindingen

1. **ORI loopt ruim 3 maanden achter.** In alle 10 gemeenten is de laatste vergadering begin juli 2026; Rotterdam heeft zelf vergaderingen tot en met oktober. Of de harvester sinds de zomer stilstaat of alleen traag is, is onbekend. Voor "wat besloot Den Haag vorige maand" is ORI dus niet genoeg.
2. **ORI heeft geen motie als soort en geen uitslag.** Alles is `MediaObject`, `AgendaItem` of `Meeting`. Moties herken je alleen aan de naam, en die verschilt per gemeente:
   - Amsterdam: '186.26 Motie Belkasmi c.s. …';
   - Den Haag: 'K.1 HvDH motie …', 'Afdoening motie …';
   - Groningen: 'M 50 … - VVD';
   - Utrecht: losse moties staan er nauwelijks in, wel 'Lijst aangenomen moties commissie …' en motielijsten.

   Aangenomen of verworpen staat niet in ORI. Daarvoor zijn besluitenlijsten of de RIS zelf nodig.
3. **De tekst is er.** Meer dan 97% van de documenten heeft tekst, dus vinden op onderwerp lukt. Volledige tekst levert wel veel bijlagen op (jaarverslagen, begrotingen). Fase 1 moet daarom op naam of soort filteren, niet op tekst alleen.
4. **CVDR is actueel en uniform.** Wijzigingen tot oktober 2026 staan erin, voor alle 10 gemeenten. Dit is de betrouwbaarste vergelijkingslaag (regels en tarieven). Twee aandachtspunten:
   - titels verschillen: Rotterdam 'Verordening parkeerregulering en parkeerbelastingen 2026', Utrecht 'parkeerbelastingen en precariobelasting';
   - er zijn veel versies per regeling, dus filteren op de geldende versie (`overheidrg.inwerkingtredingDatum` werkt als filter).
5. **Notubiz rechtstreeks was vanuit de cloudsessie niet bereikbaar.** `api.notubiz.nl` gaf een verbroken verbinding, `*.raadsinformatie.nl` gaf 403. Vanaf de NAS testen. Utrecht is iBabs, dus `ibabs.py` werkt daar waarschijnlijk zonder aanpassing (niet getest).
6. **Video en ondertitels staan niet in ORI.** Welke gemeenten Company Webcast gebruiken is niet nagekeken; dat is pas relevant bij volledige uitbreiding.
7. **Controle Rotterdam.** In ORI hebben sinds 2022 3.471 documenten 'motie' in de naam. In iBabs staan sinds 2018 6.842 moties, en ORI telt ook motielijsten en afdoeningsbrieven mee. ORI is dus bruikbaar om moties te vinden, niet om ze te tellen.

## Advies fase 1

- **Gemeenten:**
  - Amsterdam, Den Haag en Utrecht;
  - Eindhoven (groeistad, deelvervoer, parkeren);
  - Dordrecht en Vlaardingen (havenregio, kwetsbare wijken, veel moties in ORI).

  Schiedam, Tilburg en Groningen pas later: weinig vindbare moties in ORI. "Lijkt op Rotterdam" is mijn inschatting; een vaste indeling (zoals NPLV-gebieden) is niet nagelopen.
- **Bronnen per laag:**
  - **Regels:** CVDR, geldende versie, link naar de regeling, datum van inwerkingtreding. Alle 6 gemeenten.
  - **Moties:** ORI voor vinden. Per gemeente een naamregel (regex) om moties te herkennen. Tonen met datum, titel, indieners als die in de titel staan, en een link; zonder uitslag, met de melding 'uitslag: zie bron'. Uitslag alleen waar een RIS-koppeling makkelijk is (Utrecht via iBabs; Notubiz eerst testen vanaf de NAS).
  - **Cijfers:** RDW-parkeertarieven (al landelijk in `parkeren_rdw.py`).
- **Actualiteit:** de datum van de bron (ORI tot …) zichtbaar in het blok. Als ORI blijft stilstaan: Open State mailen, of direct de RIS gebruiken voor de 2-3 belangrijkste gemeenten.
- **Kosten:** geen AI. Eén nieuw script (`src/elders.py`) en een blok in `keten.js`. Werkt ook zonder werkmap.

## Open vragen voor Robert

- Akkoord met deze 6 gemeenten?
- Moties zonder uitslag tonen ('zie bron') of alleen tonen waar de uitslag bekend is?
- Fase 1 voegt code toe in `src/`: na de merge `sh nas/keur.sh` draaien, anders stopt de nachtrun op het codeslot.
