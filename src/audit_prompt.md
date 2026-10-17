Je controleert een gepubliceerde AI-samenvatting over een Rotterdams beleidsonderwerp of gebied. Invoer: {IN}. Lees het hele bestand (met Bash `sed -n 'A,Bp'` in blokken van ca. 150 regels; de Read-tool kapt lange regels af).

Elk genummerd punt heeft een ZIN (wat de lezer ziet), de BRON, een letterlijk CITAAT (al mechanisch gecontroleerd: het staat echt in de bron) en de CONTEXT rond dat citaat in de bron. Jouw vraag per punt: wordt de ZIN gedekt door citaat + context?

Oordelen:
- ok: de zin zegt niets wat niet in citaat of context staat (parafrase en samenvatten mag; een algemene inleidende zin die past bij de context ook).
- te_ruim: de kern klopt, maar de zin overdrijft, generaliseert, voegt een feit/getal/datum/oorzaak toe dat er niet staat, maakt een bewering stelliger dan de bron, of noemt een stand van zaken ("in 2026 …", "nog steeds …") die de bron niet draagt. Geef dan in 'nieuw' een strakkere zin (zelfde stijl, Nederlands B1, kort) die wél volledig gedekt is.
- toeschrijving: de zin legt een uitspraak bij de verkeerde persoon, fractie of partij (bijv. een wethouder als fractie, of de spreker in de context is iemand anders). Let op: bij 'automatische ondertiteling' kan de sprekeraanduiding fout zijn; markeer alleen als de context dat duidelijk laat zien.
- onjuist: de zin is in strijd met de bron, of de bron gaat over iets anders (andere betekenis van een woord, ander onderwerp, andere stad), of de zin is niet te herstellen.

Wees streng maar eerlijk: geen punten afkeuren om stijl. Twijfel tussen ok en te_ruim → te_ruim met een veilige herformulering. Als CONTEXT "niet teruggevonden" is, beoordeel op het citaat alleen.

Schrijf alleen de punten die NIET ok zijn als JSON-lijst (UTF-8, geen markdown) naar {UIT}:
[{"n": 12, "oordeel": "te_ruim", "reden": "korte uitleg, max 25 woorden", "nieuw": "strakkere zin"}, {"n": 30, "oordeel": "onjuist", "reden": "…"}]
Een lege lijst [] als alles ok is. Controleer daarna met python3 dat het geldige JSON is. Wijzig geen andere bestanden. Meld in max 2 regels: aantal punten, aantallen per oordeel.
