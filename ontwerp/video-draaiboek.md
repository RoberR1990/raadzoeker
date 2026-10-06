# Promovideo raadzoeker — draaiboek v4 (6-10-2026)

Ca. 85 seconden, 16:9 (1920×1080). Zelfde stijl als v1/v3: rustige animaties, tekst in beeld (werkt zonder geluid), groen/wit, voice-over (ElevenLabs, stem 'Emma' uit Roberts Voices, nieuwste model) met zachte muziek eronder. Nieuw logo (raadzaal-ring met spreekgestoelte en vergrootglas).

Kern (besluit Robert): **samenvattingen van vergaderingen**, **zoeken in alles**, **mooie pagina's per domein, onderwerp en gebied**. Verkenner en Inzichten zijn bonus: kort, vooral de Verkenner voor de wow. Rotterdamse knipoog: 'Niet lullen maar zoeken' en zoeken op Feyenoord (confetti).

| Tijd | Beeld | Tekst in beeld | Voice-over |
|---|---|---|---|
| 0–4 s | Woordenwolk van de raad bouwt op en trekt samen tot het nieuwe logo | raadzoeker | (muziek) |
| 4–8 s | Vergaderingen-pagina schuift in: 'Laatste raadsvergadering', 'Komt eraan', 'Per commissie' | Elke vergadering samengevat | Wat besprak de raad gisteren? |
| 8–13 s | Klik → samenvatting in één minuut, alinea's verschijnen | Lees het in één minuut | Raadzoeker vat elke vergadering samen, in één minuut. |
| 13–19 s | Uitgebreid: tik op een fractie → letterlijk citaat schuift open → ▶ → echt videobeeld van dat moment | Wie zei wat, letterlijk | Tik op een fractie: je leest wat ze zei en kijkt het moment terug. |
| 19–24 s | Per onderwerp: tijd, moties met uitslag (aangenomen/verworpen), tijdlijn commissie → raad | Van commissie tot besluit | Met de moties, de uitslag en waar het eerder besproken is. |
| 24–40 s | **Zoeken.** Zoekbalk; titel 'Niet lullen, maar zoeken.' Getypt: 'woonfraude' → bovenaan 'Uit de vergaderverslagen', dan alles wat gezegd is en alle stukken, grafiek per jaar. Daarna snel getypt: 'Feyenoord' → rood-witte confetti | Niet lullen, maar zoeken. | Niet lullen, maar zoeken. Zoek in alles wat de raad sinds 2018 zei en schreef: debatten, moties, brieven en raadsvoorstellen. Ook als het over Feyenoord gaat. |
| 40–58 s | **Pagina's.** Domeinen (dossierkast) → onderwerp Parkeren: kern, 'Net besproken', beloftespoor (moties en toezeggingen met status), kaart met parkeerzones. Dan Gebieden: kaart, klik Delfshaven → wat er speelt, besluiten van de wijkraden | Elk domein · elk onderwerp · elk gebied | Elk domein, onderwerp en gebied heeft een eigen pagina. Wat is er gezegd, besloten en beloofd? En wat speelt er in jouw wijk, tot aan de besluiten van de wijkraad. |
| 58–72 s | **Bonus: Verkenner.** Hele kennisgraaf, rustig inzoomen op 'Feyenoord City en stadion', buren lichten op (Stadionpark, Feijenoord …), route naar 'Parkeren' tekent zich. Flits van één Inzichten-grafiek (2 s) | Ontdek de verbanden | En wie verder wil kijken: de Verkenner laat zien hoe alles met elkaar samenhangt. |
| 72–76 s | Alles schuift weg, logo groot | raadzoeker | Raadzoeker. |
| 76–81 s | Drie regels verschijnen één voor één | Vind iedere uitspraak · bekijk de context · zie het grotere plaatje | Vind iedere uitspraak, bekijk de context, zie het grotere plaatje. |
| 81–85 s | Link groot, daaronder klein: 'Elke paar uur bijgewerkt · Vragen? RIO-groep Raadzoeker' | raadzoeker.nl | Open voor iedereen, op raadzoeker punt n l. |

Ca. 170 woorden voice-over (Nederlands, rustig tempo).

## Techniek

- Beeld: **echte opnames van de site** (Playwright, 1920×1080, met vooraf gescripte klikken, typen en inzoomen in de Verkenner), daarna in Remotion gemonteerd met tekst, overgangen, muziek en stem. Voordeel t.o.v. v1 (nagebouwde schermen): klopt altijd met de site, en de Verkenner-interactie is echt.
- Voice-over: via de ElevenLabs-website in Roberts Chrome (stem 'Emma'), per scène een los fragment downloaden (mp3), zodat beeld en stem precies aansluiten. Geen API-sleutel nodig.
- Muziek: rechtenvrij of ElevenLabs Music, zacht.
- Eerst een stille proef (beeld + tekst), daarna stem en muziek.

## Niet meer van toepassing uit v3

- Inloggen met @rotterdam.nl (site is openbaar sinds 6-10-2026).
- 'Elke bewering één klik van de bron', 'vibecode', nagebouwde schermen, levende teller.
