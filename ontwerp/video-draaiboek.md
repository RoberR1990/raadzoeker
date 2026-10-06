# Promovideo raadzoeker — draaiboek v4 (6-10-2026)

Ca. 100 seconden, 16:9 (1920×1080). Zelfde stijl als v1/v3: rustige animaties, tekst in beeld (werkt zonder geluid), groen/wit, voice-over (ElevenLabs, stem 'Emma' uit Roberts Voices, nieuwste model) met zachte muziek eronder. Nieuw logo (raadzaal-ring met spreekgestoelte en vergrootglas).

Kern (besluit Robert): **samenvattingen van vergaderingen**, **zoeken in alles**, **mooie pagina's per domein, onderwerp en gebied**. Verkenner en Inzichten zijn bonus: kort, vooral de Verkenner voor de wow. Rotterdamse knipoog: 'Niet lullen maar zoeken' en zoeken op Feyenoord (confetti).

| Tijd | Beeld | Tekst in beeld | Voice-over |
|---|---|---|---|
| 0–4 s | Woordenwolk van de raad bouwt op en trekt samen tot het nieuwe logo | raadzoeker | (muziek) |
| 4–20 s | **Vergaderingen.** Overzicht: 'Laatste raadsvergadering', 'Komt eraan', 'Per commissie'. Klik → 1-minuut-samenvatting in alinea's. Tik op een fractie → citaat schuift open → ▶ springt naar het echte videobeeld van dat moment | Gisteren vergaderd? Lees het in één minuut | Wat besprak de raad gisteren? Raadzoeker vat elke vergadering samen: in één minuut, of uitgebreid per onderwerp. Tik op een fractie en je leest wat ze letterlijk zei, en kijkt dat moment zo terug. |
| 20–30 s | Uitgebreid: per onderwerp de tijd (14:05–15:12 uur), moties met uitslag (aangenomen/verworpen), tijdlijn commissie → raad, 'Meer hierover' → dossier | Van commissie tot besluit | Je ziet hoe lang erover gepraat is, welke moties het haalden en waar het onderwerp eerder op tafel lag. |
| 30–46 s | **Zoeken.** Zoekbalk; titel 'Niet lullen, maar zoeken.' Getypt: 'woonfraude' → bovenaan 'Uit de vergaderverslagen', dan alles wat gezegd is en alle stukken, grafiek per jaar. Daarna snel getypt: 'Feyenoord' → rood-witte confetti | Niet lullen, maar zoeken. | Niet lullen, maar zoeken. Zoek in alles wat de raad sinds 2018 zei en schreef: debatten, moties, brieven en raadsvoorstellen. Ook als het over Feyenoord gaat. |
| 46–66 s | **Pagina's.** Domeinen (dossierkast) → onderwerp, bv. Discriminatie: kern, 'Net besproken', moties en toezeggingen met status. Dan Gebieden: kaart, klik Delfshaven → wat er speelt, wijken, besluiten van de wijkraden | Elk domein · elk onderwerp · elk gebied | Elk domein, onderwerp en gebied heeft een eigen pagina. Wat is er gezegd, besloten en beloofd? En wat speelt er in jouw wijk, tot aan de besluiten van de wijkraad. |
| 66–82 s | **Bonus: Verkenner.** Hele kennisgraaf, rustig inzoomen op 'Feyenoord City en stadion', buren lichten op (Stadionpark, Feijenoord …), route naar 'Parkeren' tekent zich. Flits van één Inzichten-grafiek (2 s) | Ontdek de verbanden | En wie verder wil kijken: de Verkenner laat zien hoe alles met elkaar samenhangt. |
| 82–100 s | Alles schuift weg, logo groot, regels verschijnen, link | Vind iedere uitspraak · bekijk de context · overzie het grotere plaatje · Elke paar uur bijgewerkt · raadzoeker.nl · Vragen? Robert Riteco | Raadzoeker. Vind iedere uitspraak, bekijk de context en zie het grotere plaatje. Elke paar uur bijgewerkt, open voor iedereen. Kijk op raadzoeker punt n l. |

Ca. 200 woorden voice-over (Nederlands, rustig tempo).

## Techniek

- Beeld: **echte opnames van de site** (Playwright, 1920×1080, met vooraf gescripte klikken, typen en inzoomen in de Verkenner), daarna in Remotion gemonteerd met tekst, overgangen, muziek en stem. Voordeel t.o.v. v1 (nagebouwde schermen): klopt altijd met de site, en de Verkenner-interactie is echt.
- Voice-over: ElevenLabs API, stem 'Emma', per scène een los fragment zodat beeld en stem precies aansluiten. Nodig: `ELEVENLABS_API_KEY` in `D:\Raadzoeker\.env` (staat in .gitignore).
- Muziek: rechtenvrij of ElevenLabs Music, zacht.
- Eerst een stille proef (beeld + tekst), daarna stem en muziek.

## Niet meer van toepassing uit v3

- Inloggen met @rotterdam.nl (site is openbaar sinds 6-10-2026).
- 'Elke bewering één klik van de bron', 'vibecode', nagebouwde schermen, levende teller.
