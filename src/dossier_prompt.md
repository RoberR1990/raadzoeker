Je schrijft een holistische samenvatting van één Rotterdams beleidsonderwerp voor gemeenteambtenaren, op basis van ALLEEN de bronnen in het invoerbestand {IN}. Lees het hele bestand.

Doel: snel snappen wat er speelt rond "{ONDERWERP}": wat de raad wil, wat het college heeft beloofd en gedaan, wat wijken signaleren en wat nog openstaat. Nadruk op 2022 en later; oudere bronnen alleen als achtergrond.

Regels (streng):
- Elke zin/elk punt heeft precies één broncode (zoals D12, M3, T2, V1, S5, W7) en een LETTERLIJK citaat uit die bron: 8 tot 30 woorden, exact gekopieerd, zonder iets weg te laten of te veranderen (ook geen '...' in het midden). Een script controleert dit woord voor woord en schrapt alles wat niet klopt. Het citaat wordt als controle (tooltip) getoond; de zin zelf moet zonder citaat begrijpelijk zijn.
- Schrijf alleen wat de bron zegt. Geen eigen oordelen over of beleid werkt, geen stellige conclusies, geen woorden als "helaas" of "terecht". Neutraal, zakelijk, gewone taal (B1), korte zinnen, Nederlands.
- Fracties: een standpunt hoort bij een fractie alleen als de bron van die fractie is: een debatfragment waarin een raadslid van die fractie spreekt (partij staat tussen haakjes achter de naam), of een motie/vraag die die fractie indiende. Schrijf nooit uitspraken van wethouders of de burgemeester toe aan een fractie.
- College: alleen bronnen van het college: toezeggingen (T), antwoorden van het college op schriftelijke vragen (V, citaat uit het deel na ANTWOORD VAN HET COLLEGE), raadsvoorstellen/brieven/stukken (S), of debatfragmenten waarin een wethouder of de burgemeester spreekt (D zonder partij).
- Noem bij moties en toezeggingen géén status (aangenomen, verworpen, afgedaan) in je eigen tekst; die zet het script er zelf bij uit iBabs.
- Debatfragmenten met "auto" komen uit automatische ondertiteling en kunnen fouten bevatten; citeer ze alleen als de zin goed leesbaar is.
- Negeer bronnen die over iets anders gaan dan dit onderwerp (andere betekenis van hetzelfde woord).
- Gebruik geen namen van bewoners of insprekers. Namen van raadsleden en wethouders mogen.
- Liever minder punten die kloppen dan veel punten.
- STAND VAN ZAKEN: de laatste zin van de kern, van de eerste alinea van de verdieping en van elke intro (tijdlijn, fracties, college, wijken, open) beschrijft de meest recente stand van zaken: bij voorkeur uit 2026, anders de meest recente bron, en noemt dan expliciet maand en jaar ("In juli 2026 …", "Sinds maart 2025 is er geen nieuw besluit …"). Gebruik daarvoor de nieuwste bron die over dit punt iets zegt. Zo weet de lezer bij elk onderdeel wat nu de stand is.

Een "zin" is steeds: {"zin": "…", "bron": "D12", "citaat": "…"}.

Schrijf het resultaat als JSON (UTF-8, geen markdown eromheen) naar {UIT}:
{
 "onderwerp": "{ONDERWERP}",
 "kern": [zin, …],                       // 4-6 zinnen: waar gaat het over, wat is de stand nu
 "verdieping": [[zin, …], [zin, …], …],   // 4-7 alinea's van 3-6 zinnen, samen 350-600 woorden: gaat de diepte in (achtergrond, keuzes en afwegingen, wat werkte en wat niet volgens de bronnen, spanningen tussen partijen/wijken/college, cijfers), loopt als een verhaal
 "tijdlijn": {"intro": [zin, …],         // max 5 zinnen: het verloop in het kort, eindigend met de laatste stand van zaken
              "punten": [{"datum": "JJJJ-MM-DD", "wat": "korte titel van het moment (max 15 woorden)", "bron": "M3", "citaat": "…"}]},   // 8-12 momenten
 "fracties": {"intro": [zin, …],         // max 5 zinnen: waar de fracties het over eens en oneens zijn, en de laatste stand
              "punten": [{"fractie": "VVD", "standpunten": [{"wat": "korte zin, max 20 woorden", "bron": "D40", "citaat": "…"}]}]},   // per fractie 1-3 standpunten
 "college": {"intro": [zin, …],          // max 5 zinnen: wat het college beloofde en deed, met de laatste stand
             "punten": [{"wat": "korte zin, max 20 woorden", "bron": "T2", "citaat": "…"}]},   // max 10
 "wijken": {"intro": [zin, …],           // max 5 zinnen: welke signalen terugkomen en waar
            "punten": [{"wijk": "Feijenoord", "wat": "korte zin, max 20 woorden", "bron": "W3", "citaat": "…"}]},   // max 10
 "open": {"intro": [zin, …],             // max 3 zinnen
          "punten": [{"wat": "korte zin, max 20 woorden", "bron": "T5", "citaat": "…"}]}   // max 6
}

Meld na afloop in maximaal 3 regels: aantal punten per onderdeel en wat je in de bronnen miste.
