# Promovideo raadzoeker — draaiboek v4 (6-10-2026)

Ca. 94 seconden, 16:9 (1920×1080). Zelfde stijl als v1/v3: rustige animaties, tekst in beeld (werkt zonder geluid), groen/wit, voice-over (ElevenLabs, stem 'Emma' uit Roberts Voices, nieuwste model) met zachte muziek eronder. Nieuw logo (raadzaal-ring met spreekgestoelte en vergrootglas).

Kern (besluit Robert): **samenvattingen van vergaderingen**, **zoeken in alles**, **een pagina per domein, onderwerp en gebied**, **volgen**. Verkenner en Inzichten zijn bonus. Rotterdamse knipoog: zoeken op Feyenoord (kleine confetti). Niet: 'Niet lullen maar zoeken' (te grof), 'Vind iedere uitspraak' (te vaag).

Gebouwd in Remotion (`video/src/Deel1..5.jsx`, samen `Volledig`), ca. 94 s. Voice-over per fragment (ElevenLabs, stem 'Emma'), elk als los mp3-bestand, zodat beeld en stem precies aansluiten:

| # | Tijd | Beeld | Voice-over |
|---|---|---|---|
| 1 | 0–5,5 s | Woordenwolk trekt samen tot het logo | (muziek) |
| 2 | 5,5–10 s | Vergaderingen-overzicht, Komt eraan | Wat heeft de gemeenteraad deze week besproken? |
| 3 | 10–15,5 s | Korte en uitgebreide samenvatting | Raadzoeker vat elke vergadering samen. In één minuut, of uitgebreid in tien. |
| 4 | 15,5–23 s | Fractie → citaat → echt videobeeld | Tik op een fractie: je leest letterlijk wat er is gezegd, en kijkt het moment zelf terug. |
| 5 | 23–28 s | Moties met uitslag, tijdlijn | Met de moties, de uitslag, en waar het eerder op tafel lag. |
| 6 | 28–38 s | Zoeken: woonfraude, zes soorten bronnen | Zoek in alles wat de raad sinds 2018 zei en schreef. Debatten, moties, vragen, brieven en de wijkraden. |
| 7 | 38–45 s | Vijf zoekwoorden, confetti bij Feyenoord | Over elk onderwerp. Van tramlijn tot Tweebosbuurt. |
| 8 | 45–49 s | Domeinen | Elk domein, onderwerp en gebied heeft een eigen pagina. |
| 9 | 49–54 s | Parkeren: volgen, net besproken, beloofd | Wat is er gezegd, besloten en beloofd? Volg een onderwerp, en je krijgt een seintje bij nieuws. |
| 10 | 54–60 s | Delfshaven, besluiten van de wijkraden | En wat speelt er in jouw wijk, tot aan de besluiten van de wijkraad. |
| 11 | 60–73 s | Verkenner: vlucht over clusters, route Feyenoord City → Parkeren | Wie verder wil kijken: de Verkenner laat zien hoe alles samenhangt. Van veiligheid tot wonen, en van Feyenoord City tot parkeren. |
| 12 | 73–81 s | Inzichten: per jaar, Waar speelt wat? | Inzichten zet de cijfers op een rij. Waar speelt wat? |
| 13 | 81–89 s | Logo en vier kernpunten | Raadzoeker. Elke vergadering samengevat, zoeken in alles, een pagina per onderwerp, en volg wat jou raakt. |
| 14 | 89–94 s | raadzoeker.nl, RIO-groep | Open voor iedereen, op raadzoeker punt n l. |

Ca. 175 woorden (Nederlands, rustig tempo).

## Techniek

- Beeld: **echte opnames van de site** (Playwright, 1920×1080, met vooraf gescripte klikken, typen en inzoomen in de Verkenner), daarna in Remotion gemonteerd met tekst, overgangen, muziek en stem. Voordeel t.o.v. v1 (nagebouwde schermen): klopt altijd met de site, en de Verkenner-interactie is echt.
- Voice-over: via de ElevenLabs-website in Roberts Chrome (stem 'Emma'), per scène een los fragment downloaden (mp3), zodat beeld en stem precies aansluiten. Geen API-sleutel nodig.
- Muziek: rechtenvrij of ElevenLabs Music, zacht.
- Eerst een stille proef (beeld + tekst), daarna stem en muziek.

## Niet meer van toepassing uit v3

- Inloggen met @rotterdam.nl (site is openbaar sinds 6-10-2026).
- 'Elke bewering één klik van de bron', 'vibecode', nagebouwde schermen, levende teller.
