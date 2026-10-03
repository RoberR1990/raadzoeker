Je schrijft een holistische samenvatting van één Rotterdams beleidsonderwerp voor gemeenteambtenaren, op basis van ALLEEN de bronnen in het invoerbestand {IN}. Lees het hele bestand.

Doel: in 3 minuten snappen wat er speelt rond "{ONDERWERP}": wat de raad wil, wat het college heeft beloofd en gedaan, wat wijken signaleren en wat nog openstaat. Nadruk op 2022 en later; oudere bronnen alleen als achtergrond.

Regels (streng):
- Elke bewering heeft precies één broncode (zoals D12, M3, T2, V1, S5, W7) en een LETTERLIJK citaat uit die bron: 8 tot 30 woorden, exact gekopieerd, zonder iets weg te laten of te veranderen (ook geen '...' in het midden). Een script controleert dit woord voor woord en schrapt alles wat niet klopt.
- Schrijf alleen wat de bron zegt. Geen eigen oordelen over of beleid werkt, geen stellige conclusies ("het probleem is opgelost"), geen woorden als "helaas" of "terecht". Neutraal, zakelijk, gewone taal (B1), korte zinnen, Nederlands.
- Fracties: een standpunt hoort bij een fractie alleen als de bron van die fractie is: een debatfragment waarin een raadslid van die fractie spreekt (partij staat tussen haakjes achter de naam), of een motie/vraag die die fractie indiende. Schrijf nooit uitspraken van wethouders of de burgemeester toe aan een fractie.
- College: alleen bronnen van het college: toezeggingen (T), antwoorden van het college op schriftelijke vragen (V, citaat uit het deel na ANTWOORD VAN HET COLLEGE), raadsvoorstellen/brieven/stukken (S), of debatfragmenten waarin een wethouder of de burgemeester spreekt (D zonder partij).
- Debatfragmenten met "auto" komen uit automatische ondertiteling en kunnen fouten bevatten; citeer ze alleen als de zin goed leesbaar is.
- Gebruik geen namen van bewoners of insprekers. Namen van raadsleden en wethouders mogen.
- Liever minder punten die kloppen dan veel punten.

Schrijf het resultaat als JSON (UTF-8, geen markdown eromheen) naar {UIT}:
{
 "onderwerp": "{ONDERWERP}",
 "kern": [{"zin": "…", "bron": "D12", "citaat": "…"}],            // 4-6 zinnen: waar gaat het over, wat is de stand nu
 "tijdlijn": [{"datum": "JJJJ-MM-DD", "wat": "…", "bron": "M3", "citaat": "…"}],   // 6-10 belangrijke momenten, oud naar nieuw (datum = datum van de bron)
 "fracties": [{"fractie": "VVD", "standpunt": "…", "bron": "D40", "citaat": "…"}],  // de fracties die er echt iets over zeggen, max 2 per fractie
 "college": [{"belofte": "…", "stand": "…", "bron": "T2", "citaat": "…"}],          // wat het college beloofde/deed; "stand" = status uit de bron (bijv. afgedaan op …, of onbekend)
 "wijken": [{"wijk": "Feijenoord", "signaal": "…", "bron": "W3", "citaat": "…"}],    // wat wijkraden aankaarten, max 8
 "open": [{"wat": "…", "bron": "T5", "citaat": "…"}]                                // openstaande toezeggingen/moties/vragen, max 6
}

Meld na afloop in maximaal 3 regels: aantal punten per onderdeel en wat je in de bronnen miste.
