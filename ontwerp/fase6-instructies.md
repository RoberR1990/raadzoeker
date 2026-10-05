# Fase 6: de raadzoeker werkt zichzelf bij op de NAS

Stand 5-10-2026. Alles staat klaar op de NAS in `/volume1/docker/raadzoeker/`: de container-bestanden (`nas-build/`), `compose.yaml`, de werkmap met gegevens (`werk/`) en een eigen sleutel (`ssh/`). De container haalt bij de eerste start de code op van GitHub en draait daarna volgens een vast schema.

## Wat jij moet doen (eenmalig, ca. 10 minuten)

1. **Sleutel op GitHub zetten**, zodat de NAS mag pushen. GitHub → repository `raadzoeker` → *Settings* → *Deploy keys* → *Add deploy key*:
   - Title: `NAS bijwerker`
   - Key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBO86CSjjzVE2Av5hmItZFhlIZLaqiunAd7ZJSE6Uz4u raadzoeker-nas`
   - Vink **Allow write access** aan.
2. **Container starten** in DSM: *Container Manager* → *Project* → *Maken* → naam `raadzoeker`, pad `/volume1/docker/raadzoeker`, gebruik de bestaande `compose.yaml` → *Volgende* → *Gereed*. Daarna bij het project **Bouwen** en vervolgens **Starten** (Bouwen alleen start de container niet).
3. (Optioneel) Melding op je telefoon als een run mislukt: installeer de app *ntfy*, abonneer je op een eigen, moeilijk te raden onderwerp (bijvoorbeeld `raadzoeker-` gevolgd door wat willekeurige letters) en vul dat in `compose.yaml` in bij `NTFY=`.

Daarna kan ik via SSH de logboeken lezen (`/volume1/docker/raadzoeker/werk/logs/`) en de eerste runs controleren.

## Wat er automatisch gebeurt

| Wanneer | Wat |
|---|---|
| Elke nacht 02:30 | iBabs: nieuwe stukken én de nog openstaande moties en toezeggingen opnieuw bekijken (status, tussenberichten, afdoening); schriftelijke vragen met antwoord; raadsvoorstellen; Gemeenteblad (deze en vorige maand); zoekindex; domein- en gebiedslabels; alle dossiers, voorbeelddossiers en het Lab. Daarna online (git push → Cloudflare). |
| Werkdagen 09:15, 12:15, 15:15, 18:15, 21:15 | iBabs-lijsten en nieuwe moties, toezeggingen en brieven, en de pagina's die daarvan afhangen. Zo staan moties en stemmingen van een raadsvergadering dezelfde avond op de site. |

Mislukt een stap, dan wordt er niets online gezet: de site blijft op de vorige versie en 'bijgewerkt t/m' laat dat zien. De status staat in `werk/status.json` en op de site in `data/status.json`.

## Wat nog niet automatisch gaat

- **Nieuwe debatten.** De notulen en ondertiteling zijn eenmalig verzameld (deels via de browser). Voor automatisch ophalen is nog een ophaler nodig voor de ondertiteling van nieuwe vergaderingen (Company Webcast) en de notulen. Tot die tijd loopt 'Gezegd' tot 2 oktober 2026.
- **Wijkraadvergaderingen en hun bijlagen**: de ophalers lezen nu uit een cache; dat moet eerst worden aangepast.
- **Antwoorden op schriftelijke vragen die later komen**: nieuwe vragen komen erbij, maar een antwoord op een al opgehaalde vraag nog niet.
- **AI-samenvattingen**: bewust niet automatisch. Bijwerken kost tokens en moet met de hand, zoals afgesproken in fase 6 (alleen aanvullen als er nieuwe stukken in vallen).

## Kan het nog vaker, en heeft dat zin?

- **Heeft het zin?** Beperkt. De raad vergadert op donderdag, commissies op woensdag en donderdag. Moties en stemuitslagen staan meestal dezelfde avond in iBabs; brieven en antwoorden komen verspreid over de werkdag. Elke 3 uur op werkdagen plus elke nacht vangt dat goed. Elk uur levert vooral runs op waarin niets verandert.
- **Kan het technisch?**
  - iBabs: ja. Een lichte run vraagt een paar honderd pagina's op, 1 per seconde, en duurt 5 tot 10 minuten.
  - Cloudflare Pages (gratis): maximaal 500 keer online zetten per maand. Elk uur zou ca. 720 keer zijn en dus te veel. Het huidige schema zit op ca. 140, en een run waarin niets verandert zet niets online.
  - De NAS heeft genoeg rekenkracht. De nachtrun duurt naar schatting 1 tot 1,5 uur, vooral door het verversen van de openstaande stukken.
- **Als het echt sneller moet**, bijvoorbeeld tijdens een raadsvergadering, dan kan een extra run op donderdagavond (20:00 en 23:00).
- **Nog sneller** kan pas als de gegevens los van de site worden gezet (bijvoorbeeld in Cloudflare R2), zodat bijwerken geen nieuwe versie van de site vraagt. Dat is pas zinvol als de raadzoeker breder gebruikt wordt.

## Kosten

Zonder AI kost bijwerken niets, alleen stroom van de NAS. De AI-kosten komen alleen bij nieuwe of bijgewerkte samenvattingen. Uit deze sessie: een uitgebreide samenvatting kost 0,5 tot 0,85 miljoen Opus-tokens per dossier; het akkoord kostte 0,18 miljoen. Een meting over een week, zoals het plan vraagt, kan zodra de nachtelijke run draait: dan tellen we hoeveel nieuwe stukken er per dossier binnenkomen.
