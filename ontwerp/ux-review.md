# UX/UI-review Raadzoeker (startpagina, dossier, briefing) — 3 oktober 2026
Door een UX-subagent; volgorde = prioriteit.

## P1 — Visuele hiërarchie en typografie
- Mis: h1-h4 op 800; getallen 44px/800 en 34px/800; vette titels in Net besloten en vette trefwoorden in Wat komt op. Elk blok heeft een eigen blikvanger.
- Waarom: vet werkt alleen als contrast. Arial kent alleen 400/700, dus 800 wordt 700; het verschil moet uit grootte en ruimte komen.
- Oplossing: h1 40/48px (mobiel 30), 700, regelhoogte 1.1, alleen voor de zoekvraag. h2 24/700, h3 18/700, tekst 16/1.5/400, meta 14/400, kleine lettertjes 13. Grote getallen 40px/400 met tabulaire cijfers. Lijsttitels 400, alleen onderstreept als het een link is. Eén vet element per blok. Hooguit één groen gevuld vlak per scherm.

## P1 — Rust en witruimte
- 8px-raster: 64px tussen secties (mobiel 40), 24px tussen blokken, 24/32px binnen een vlak, maximaal 65ch breed.
- Startpagina in lagen: (1) zoekvraag en zoekveld, zonder iets ernaast dat concurreert; (2) Net besloten als witte lijst met een groene bovenrand van 4px, 3 items en 'Alle besluiten'; (3) kaart; (4) één kaderloze strook 'Signalen': beloftemonitor als zin, woorden in 400 met een grijze sparkline en groen eindpunt, briefing als tekstlink; (5) Wrapped naar Lab.

## P1 — Mijn dossier: context
- Uitklapbare rij met `<details>`.
- Motie: eerste zin van het dictum na 'verzoekt' (geen AI), fracties als neutrale tags, stembalk voor/tegen, statuslijn ingediend → aangenomen → afdoening verwacht → afgedaan, link naar het debat.
- Toezegging: wethouder, commissie, termijn en 'x dagen over de termijn' (oranje stip met tekst).
- Debat: raad of commissie, agendapunt, 1-2 letterlijke fragmenten met de term gemarkeerd op --groen-zacht, sprekers, link naar het videomoment.
- Filterchips Open / Over de termijn / Afgedaan, plus sortering. Cijfertegels op 400; alleen 'over de termijn' krijgt een oranje accent.

## P1 — Kaart
- Water (Maas, havens) in #CFE3EF, nooit groen. Havens in --grijs2 met arcering en labels van 12px. Maasvlakte als inzetkaart of afgesneden met een pijl.
- 6-8 labels op de kaart (13px met witte halo). Legenda met 5 discrete klassen en grenswaarden. Geselecteerd gebied: zwarte rand van 2px.
- Jaartal 40px/400 linksboven in de kaart. Afspeelknop met aria-pressed, overgangen van 400ms.
- Hover gekoppeld aan de ranglijst; klikken opent een paneel met trend, top 3 onderwerpen en een link naar het Wijk-scherm.
- Toetsenbord: tabindex=0, role=button, aria-label met de waarde. Knop 'Toon als tabel'. Mobiel: volle breedte, uitschuifpaneel, schuifhendel van 44px.

## P2 — Navigatie
- Logo = home · Onderwerpen · Wijken · Briefing · Archief; rechts in 14/400: Lab (experimenteel) · Over. Zoekknop in de balk, kruimelpad, kruisverwijzingen tussen onderwerp, wijk en briefing.
- Slug-URL's (#wonen). Over-pagina voor bronnen, methode, stand van de data, onofficieel-verklaring en contact.

## P2 — Logo
1. Woordmerk 'raadzoeker' in kleine letters, Bolder 700, met 'oo' als loep.
2. Halfrond van 9 stippen (raadzaal), één groen, naast het woordmerk in 400; werkt goed als favicon.
3. Afgerond vierkant met ‘ ('wat de raad zei').
- Geen wapen of leeuw, altijd 'onofficieel' (13px) erbij. Advies: 2 of 3 met het woordmerk.

## P2 — Toegankelijkheid
- Focusring: outline 3px #000 plus box-shadow 0 0 0 6px #fff. Hover via text-decoration-thickness 2px in plaats van groene tekst.
- Gele stip een donkere rand (nu 1,9:1, minimaal 3:1). Rood → oranje (#E30613 zit niet in het datapalet).
- Combobox: aria-expanded, role=option, aria-activedescendant. Tabs: role=tab, aria-selected, pijltjestoetsen. Klikdoelen minimaal 44px.
- Witte tekst op groen alleen vanaf 14px en zonder opacity. Trendgrafiek met een verborgen tabel als alternatief.

## P2 — Mobiel
- Onder 700px: logo, zoekicoon en Menu. Startpagina gestapeld, Net besloten 3 items. Op het dossier 'Wat staat er open' vóór de AI-samenvatting. Briefing als leesweergave met 'Pdf maken'.

## P3 — Briefing
- Datum 'Stand' prominenter, QR-code of korte URL onderaan, dictum van de motie op 1 regel, minder tussenlijnen.

## Wow (kies 3)
1. Deelkaart 1200×630 met voorbeeldweergave in Teams.
2. Stemhalfrond per motie.
3. Kaart speelt bij binnenkomst één keer 2018→2025 af (behalve bij reduced-motion).
4. Citaat 'deze week, vijf jaar geleden' in 32px/400 met enkele aanhalingstekens.
5. Beeswarm van moties per onderwerp, met status als kleur.
