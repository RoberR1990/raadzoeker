# Fase 0 — inventarisatie (4-10-2026)

Stand bij commit `8908af8`. Alles hieronder is vandaag nagekeken in de repo, de werkmap en de lokale site.

## 1. Stack en mappen

- **Geen database.** Statische site (HTML + JS, geen framework) op Cloudflare Pages; data als JSON, zstd-gecomprimeerd (`.zst`). Pijplijn in Python 3.12 op Roberts pc, handmatig gestart.
- `src/` — 50 scripts (ophalen, uitlezen, bouwen, controleren). `docs/` — de site (132 MB). `data/` — AI-samenvattingen. Werkmap `D:\Downloads Chrome\raadzoeker-werk` — ruwe bronnen en tussenbestanden (ca. 1 GB+).

## 2. Data ("tabellen") met aantallen

| Bestand | Inhoud | Aantal |
|---|---|---|
| `docs/data/raad/JAAR.zst` | raadsvergaderingen 2018–2026 | 177 vergaderingen, 116.820 spreekbeurten, 10,3 mln woorden, 6.468 moties uit notulen, 454 toezeggingen (herkend op formulering) |
| `docs/data/commissies/JAAR.zst` | commissievergaderingen 2022–2026 (ondertitels) | 764 vergaderingen, 149.781 spreekbeurten, 22 mln woorden |
| `docs/data/ibabs/stukken.zst` | officiële stukken iBabs + rekenkamer/ombudsman/wijkraden | 31.597 (o.a. 10.522 brieven, 6.842 moties, 6.556 toezeggingen, 4.425 vragen, 950 collegebesluiten, 802 raadsvoorstellen, 783 wijkraadadviezen) |
| `docs/data/ibabs/moties.json` | koppeling motie in notulen ↔ iBabs | 5.882 van 6.297 (93%) |
| `docs/data/tekst/` | volledige-tekstindex | 44.505 stukken (75 MB, 512 shards) |
| `docs/ontwerp/*.json` | dossiers (41 thema's), onderwerpen (38), wijken (71), kaart, lab, start | — |
| `data/sum/`, `data/tsum/` | AI-samenvattingen per debat (2026) en per thema | 137 / 40 |
| `docs/ontwerp/samenvattingen/` | AI-onderwerpsamenvatting (Opus, citaatgecontroleerd) | 3: deelscooters, parkeeroverlast, explosies |
| werkmap `wijk/` | bekendmakingen, Wijkprofiel, politie, wijkraadvergaderingen + 12.673 bijlagen | ca. 92.000 bekendmakingen |

## 3. Wat er op de site staat en of het werkt

Alle pagina's vandaag lokaal geladen zonder JS-fouten.

- **Live en werkend:** `raadzoeker.html` (raad 2018–2026), `commissiezoeker.html` (2022–2026). `index.html` linkt alleen naar deze twee.
- **Ontwerp (v2, ook online maar niet gelinkt vanaf index):** `startpagina` (kaart, signalen, Wrapped), `dossier` = **Onderwerpen in indeling C** (sterk; wordt de basis), `briefing` (A4, sterk; wordt de exportknop), `wijk`, `lab`, `over`, `zoek` (alle 44.505 stukken).
- **Rommel om op te ruimen in fase 3:** 3 doorverwijspagina's `commissiezoeker-20xx`, `samenvatting.html` en `schetsen.html` (proefpagina's), `src/oud/`.

## 4. Pijplijn: hoe en wat het kost

- **Volledig handmatig.** Geen planning, niets op de NAS. Publiceren = `git push` (Cloudflare bouwt zelf).
- Bouwen uit bronnen: ca. 10 min (`maak.py alles`); alleen pagina's: seconden. `teksten.py` opnieuw na elk ophaalblok.
- Ophalen iBabs: 1 verzoek/sec, hervatbaar in blokken van 9 min. Volledige eerste ophaalronde kostte meerdere sessies; bijwerken alleen-nieuw is er nog niet.
- **Tokens:** de bouw zelf gebruikt geen AI. AI alleen voor samenvattingen: onderwerp ca. 300–400k Opus-tokens; thema (Haiku) klein. Per nieuw stuk labelen/samenvatten bestaat nog niet, dus geen meting.

## 5. Bestaande indelingen (belangrijkste bevinding)

- **iBabs geeft zelf een `Beleidsveld` per stuk**: brieven 100%, toezeggingen 100%, raadsvoorstellen 100%, vragen 99%, moties 94%. Ca. 20 echte waarden (Bouwen en Wonen 5.075, Mobiliteit 2.810, Veiligheid 2.749, Zorg 2.493, Buitenruimte 2.303, Economie, Cultuur, Onderwijs, Duurzaam, Samenleven, Armoedebestrijding, Bestuur, Organisatie, Werk en Inkomen, Sport, Haven, Welzijn, Wijken, …) plus spellingvarianten en historische namen (Duurzaamheid→Duurzaam, 3× Financiën, Integratie tot 2022). → **Fase 1b is grotendeels methode "bron"**, geen model nodig voor ~95% van de iBabs-stukken.
- **Ook een `Commissie` per stuk** (brieven, vragen, raadsvoorstellen bijna altijd; moties/toezeggingen ~55%), met afkortingen en jaartallen. Drie indelingen zichtbaar:
  - 2018–2022: ZOCS, EDEM, BWB, VB, WIISA, MPOF (+ 3 tijdelijke)
  - 2022–2026: BWB, MHEK, BOFV, ZWCS, WIOSSAN (+ 3 tijdelijke)
  - 2026–: Bouwen & Wonen, Leefomgeving & Economie, Veiligheid Bestuur & Financiën, Zorg & Cultuur, Onderwijs & Samenleven (+ Werk & Inkomen?)
- **Commissievergaderingen** hebben hun commissie al (veld `cats`), dus domein via bron.
- **Gaten:** raadsdebatten (spreekbeurten) hebben geen beleidsveld → via gekoppeld stuk of agendapunttitel; collegebesluiten en externe rapporten ook niet.
- **Al in de code:** `themes.py` = 41 trefwoordthema's in precies de drie assen van het plan (15 *Beleidsdomeinen*, 11 *Thema's dwars door de organisatie*, 15 *Wijken en gebieden*); `onderwerpen.py` = 38 onderwerpen onder die thema's. Op trefwoord, dus "genoemd", niet "hoofdonderwerp", en zonder zekerheid.

## 6. Inlog

- Cloudflare Access voor de hele site (toegelaten e-mailadressen; regel naar @rotterdam.nl afgesproken). Geen eigen accounts.
- **Stemmen kan niet op een puur statische site.** Nodig: opslag + server. Kleinste route: Cloudflare Pages Functions + D1; Access geeft dan het e-mailadres mee (`Cf-Access-Authenticated-User-Email`). NAS kan ook, maar zit niet achter Access.

## 7. Spanningen met het plan

1. Plan spreekt van tabellen; hier zijn het bestanden. Labels/gebieden worden extra JSON in de pijplijn — prima, maar ideeën/stemmen vragen wél een echte opslag (zie 6).
2. Gebiedscommissies (tot 2022) zijn nog niet opgehaald; vertaaltabel 2b kan pas daarna.
3. Raad-spreekbeurten krijgen geen bron-domein; hier is een model (of koppeling via agendapunt) nodig.
4. Nachtelijke run op de NAS: NAS moet dan kunnen pushen naar GitHub; docker-CLI werkt niet via SSH (alleen Container Manager).
