# Promovideo raadzoeker — draaiboek v3 (5-10-2026)

60 seconden, 16:9 (1920×1080). Geanimeerd met echte data van de site, geen schermopname. Tekst in beeld (werkt ook zonder geluid), voice-over via ElevenLabs (nieuwste model, nu Eleven v3), zachte muziek eronder. Open source: repository wordt openbaar met MIT-licentie (besluit Robert).

| Tijd | Beeld | Tekst in beeld | Voice-over |
|---|---|---|---|
| 0–3 s | Woordenwolk 2026 (echte woorden uit de raad) bouwt op, woorden vliegen naar het midden en worden één lege zoekbalk | — | (alleen muziek) |
| 3–11 s | De vraag wordt getypt. Resultaten met gemarkeerde woorden, grafiek 'per jaar' groeit, klik op '▶ Bekijk dit moment' → videobeeld | Wat zei de raad over parkeren? | Wat zegt de Rotterdamse raad eigenlijk over parkeren? Zoek in alles wat er is gezegd en geschreven, en spring meteen naar het moment in de vergadering. |
| 11–20 s | De zoekbalk wisselt snel van vraag (jeugdzorg, woningbouw, haven, overlast). Daarna de matrix domeinen × gebieden die vakje voor vakje oplicht, en een tijdlijn 2018 → 2026 | 13 domeinen · 14 gebieden · 8 jaar raad | En dat voor elk onderwerp: dertien domeinen, veertien gebieden, acht jaar debatten, moties en stukken. |
| 20–30 s | Dossier Parkeren: de kern, een zin licht op en toont het letterlijke citaat met bron; daarna de punten uit het coalitieakkoord | Elke zin één klik van de bron | Elk dossier vertelt het hele verhaal: wat er is gezegd, wat er is besloten en wat het coalitieakkoord belooft. |
| 30–37 s | Beloftespoor: toezeggingen en moties schuiven van 'open' naar 'afgedaan', stemtabel per fractie flitst langs | Volg de beloftes | En je ziet of die beloftes ook worden nagekomen. |
| 37–50 s | Gebiedenkaart, klik op Delfshaven, inzoomen. Gebiedspagina: waar de raad over praat (per jaar), de wijken, wat de wijkraad adviseert, een paar wijkcijfers naast elkaar, één Lab-grafiek | Wat speelt er in jouw wijk? | Of kies je eigen gebied. Wat speelt er in Delfshaven, waar praat de raad over, en wat vraagt de wijkraad? |
| 50–60 s | Alles schuift weg, logo, regels verschijnen, link | Elke bewering één klik van de bron · Elke paar uur bijgewerkt · Vibecode-experiment · open data · open source · Inloggen met je @rotterdam.nl-adres · [link] | Raadzoeker. Altijd actueel, elke paar uur bijgewerkt. Een open source experiment op open data. Log in met je Rotterdamse mailadres en probeer het zelf. |

Ca. 125 woorden voice-over.

## Techniek

- Remotion (React → mp4), lokaal op D:. Nagebouwde schermen in de stijl van de site, gevuld met de echte JSON.
- Voice-over: ElevenLabs API, Nederlandse stem, per scène een los fragment.
- Muziek: ElevenLabs Music of rechtenvrij nummer.
- Eerst een stille proefversie (beeld + tekst), daarna stem en muziek.

## Vóór publicatie

- Repository openbaar met MIT-licentie: eerst de git-geschiedenis nalopen op sleutels en persoonsgegevens.
- Cloudflare Access: regel naar alle @rotterdam.nl-adressen.
- Naam definitief (zie gesprek).

## Feedback Robert op proef v1 (5-10-2026), te verwerken in v2

- Totaal max. 90 seconden.
- Woordenwolk 4 s.
- Titel boven de zoekbalk: 'Wat zei de raad over …' (het woord parkeren staat al in de zoekbalk).
- 'Bekijk dit moment': echt beeld van het debat erbij (videoframe van de vergadering), niet alleen een nagebouwde speler.
- 'Elk onderwerp, elk gebied': rustiger, en duidelijker uitleggen wat de kolommen (gebieden) en rijen (domeinen) zijn.
- Slot: geen 'elke bewering één klik van de bron' (te technisch), maar iets als 'Vind iedere uitspraak · bekijk de context · overzie het grotere plaatje'. Woord 'vibecode' weg. Klein: 'Vragen? Robert Riteco'.
- Eventueel de samenhang-mindmap (samenhang.html) in de video.
