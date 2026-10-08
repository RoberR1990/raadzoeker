# Meten: wat, waarom en hoe lees je het

Meetlaag: `docs/meet.js` (Umami). Installatie: `nas/umami/README.md`. Test: `node src/test_meet.js` (jsdom, zie kop van het bestand). Zolang `CONF.host` en `CONF.id` in `meet.js` leeg zijn, meet de site niets en blijft de privacytekst op Over verborgen.

## Wat Umami te zien krijgt (en wat niet)

- Pagina's als **virtueel pad**, nooit de echte URL: `/dossier/<slug>`, `/gebied/<slug>`, `/wijk/<slug>`, `/briefing/<slug>`, `/zoeken`, `/inzichten`, `/beloofd`, `/vergaderingen`, `/verkenner`, `/volg`, `/nieuw`, `/hulp`, `/over`. Geen zoekterm, geen hash, geen query; alleen `utm_source`, `utm_medium` en `utm_campaign` blijven staan. Een referrer van de eigen site wordt teruggebracht tot het pad. Dit gebeurt in `rzMeetVoorVerzenden` en geldt voor elke verzending, ook van de tracker zelf.
- **Nooit**: zoektermen (die staan anoniem in de D1-zoeklog), sprekers, fracties, namen, e-mailadressen (`schoon()` vervangt ze en lange cijferreeksen), of tekst uit debatten. Fractie- en spreker-filters in de hash worden genegeerd.
- Geen cookies en geen eigen bezoeker-id. Uitzetten kan met `?meet=uit` (blijvend), de knop op Over, Do Not Track of `umami.disabled`.

## Gebeurtenissen

| naam | velden | wanneer |
|---|---|---|
| pageview | (pad) | laden, en bij hashchange als het virtuele pad verandert |
| zoek | n, leeg, woorden, exact, of, tab | 3 s na de laatste zoekopdracht (zelfde debounce als de zoeklog) |
| zoek_tab | tab | wissel Gezegd/Stukken |
| resultaat_open | pagina | een zoekresultaat uitklappen |
| video | pagina | 'Bekijk dit moment' |
| kopieer | soort (citaat, link, verw, copilot), pagina | klik op een kopieerknop (klik, niet gelukt-of-niet) |
| deel | kanaal (mail, teams, whatsapp, kopie), pagina, slug | deelknop; de links krijgen `utm_source=deel&utm_medium=<kanaal>` |
| volg | slug, aan | ☆ Volg / ★ Volgend |
| briefing | actie (pdf, word), slug | briefing exporteren |
| beloofd_csv | | csv-export op Beloofd |
| inzicht | actie (afbeelding, link), grafiek | Inzichten: kopieer als afbeelding of link |
| verkenner | actie (verras, route, afbeelding, deel) | Verkenner |
| weergave | pagina + d, g, van, tot, k, tab, soort, domein, gebied, thema, onderwerp, status, blok, orde | filters in de hash op Inzichten, Beloofd, Zoeken, Vergaderingen (800 ms gedempt) |
| uitklap | blok, slug | blok op een dossierpagina openklappen |
| uitgaand | doel (ibabs-raad, ibabs-wijkraad, video, rekenkamer, overheid, github, anders de host), pagina | klik op een externe link |
| tour | actie (start, stop, klaar), pagina, stap, van | rondleiding |
| welkom | keuze (ja, later, nee) | welkomstvenster |
| fout_open, fout_gemeld | pagina | fout-melden-venster (zonder tekst) |
| ei | naam | easter egg afgegaan |
| (geen naam) | | Core Web Vitals (LCP, INP, CLS) via `data-performance`; Umami toont ze in een eigen prestatierapport, niet als gebeurtenis |

## Wat je ermee kunt zien

Stel in Umami in (Rapporten → Funnels / Doelen / Reizen / UTM):

1. **Van zoeken naar bron** (funnel): `/zoeken` → `zoek` → `resultaat_open` → `uitgaand` (doel ibabs-raad of video). Laat zien of 'antwoord eerst, bron één klik dieper' werkt. Filter `zoek` op `leeg=true` voor het aandeel zoekopdrachten zonder resultaat; de woorden zelf staan in D1: `SELECT q, n, dag FROM zoeklog WHERE n = 0 ORDER BY id DESC LIMIT 100`.
2. **Verspreiding** (UTM-rapport): bezoek met `utm_source=deel`, uitgesplitst naar medium, tegenover `deel`-gebeurtenissen per kanaal. Dat is de maat voor het virale doel: hoeveel gedeelde links leiden echt tot een bezoek, en via welk kanaal. Alleen links uit de deelknoppen dragen een label; een gekopieerde link of een link uit 'Kopieer voor Copilot' niet.
3. **Hoe wordt het gebruikt** (doelen): `kopieer` met soort=copilot (wordt Copilot-gebruik echt iets?), `volg`, `briefing`, `beloofd_csv`, `inzicht`. Per pagina uit te splitsen.
4. **Welke dossiers en gebieden leven** (pagina's): top `/dossier/…`, `/gebied/…`, `/wijk/…`; per week voor trends. Dit is een rechtstreekse stadspols onder ambtenaren, maar leest alleen als aandacht van collega's, niet als aandacht voor het onderwerp zelf.
5. **Onboarding**: `welkom` (ja/later/nee) → `tour` start → klaar, plus afhakers per `stap`.
6. **Zwaar voor telefoons?** De prestatiemetingen per pagina, apparaat en browser; relevant omdat commissies ca. 550 MB geheugen gebruiken (CLAUDE.md).
7. **Waar haken mensen af?** Reizen (Journeys) vanaf `/` en vanaf `/zoeken`; terugkomers via Retentie.

## Beperkingen, eerlijk

- **Bezoekers zijn een ondergrens.** Zover bekend bepaalt Umami een sessie uit netwerkadres, browser en een rouleerzout, zonder id op het apparaat (niet nagegaan voor de versie die gaat draaien). Collega's achter hetzelfde netwerkadres met dezelfde browserversie kunnen dus als één bezoeker tellen. Gebeurtenissen en paginaweergaven blijven wel kloppen. Een eigen bezoeker-id in localStorage zou dit oplossen, maar valt onder de regels voor opslag op het apparaat; dat is een bewuste keuze die nog niet is gemaakt (privacycheck).
- Niet gemeten: wie Do Not Track, de uit-knop of een ad-blocker gebruikt. Bots filtert Umami zelf.
- `kopieer` telt klikken, niet of het klembord het deed. Kopiëren met het toetsenbord telt niet.
- `uitgaand` meet de klik, niet of de bron daarna geladen werd. De sprong naar de video via het eigen venster telt als `video`.
- Of `data-performance` in jouw Umami-versie werkt, is niet nagegaan; zo niet, dan blijven die metingen gewoon weg.

## Volgende stap (nog niet gebouwd)

Een wekelijkse samenvatting van Umami (API) naar `docs/data/gebruik.json` door de NAS-run, met een tegel op Inzichten ('Hoe wordt raadzoeker gebruikt'): alleen totalen en toppen van dossiers, geen zoektermen. Vraagt een API-sleutel op de NAS en een keuze wat openbaar mag.
