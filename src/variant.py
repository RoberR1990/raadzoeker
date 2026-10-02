
def apply(t,meta):
    R=[
     ('<h1><a id="home" href="#" title="Naar de startpagina">Raad<span>zoeker</span></a></h1>','<h1><a id="home" href="#" title="Naar de startpagina">Commissie<span>zoeker</span></a></h1>'),
     ('<div class="sub">Zoek in wat er in de Rotterdamse gemeenteraad is gezegd, <span id="span">2018–2026</span></div>','<div class="sub">Zoek in wat er in de Rotterdamse raadscommissies is gezegd, <span id="span"></span></div>'),
     ('<title>Raadzoeker – wat er in de Rotterdamse raad is gezegd</title>','<title>Commissiezoeker – wat er in de Rotterdamse raadscommissies is gezegd</title>'),
     ("<h2>Wat is er in de Rotterdamse raad gezegd?</h2>","<h2>Wat is er in de raadscommissies gezegd?</h2>"),
     ("Doorzoek letterlijk wat raadsleden, wethouders en de burgemeester sinds 2018 in de gemeenteraad hebben gezegd. Vind het citaat, zie wie het zei, lees het debat eromheen en kopieer het met bron.","Doorzoek wat raadsleden, burgercommissieleden en wethouders in de commissievergaderingen hebben gezegd. De tekst is de automatische ondertiteling van de uitzendingen: goed om te vinden wat er besproken is en naar het moment in de video te springen, niet om blind uit te citeren."),
     ("""'<button type="button" data-view="m"><i>3</i><b>Stemmingen en toezeggingen</b><span>'+nf(T.moties||0)+' moties en voorstellen met uitslag, en '+nf(T.toez||0)+' toezeggingen van het college op een rij.</span></button>'""","""'<button type="button" data-view="z"><i>3</i><b>Toezeggingen</b><span>'+nf(T.toez||0)+' toezeggingen van collegeleden in de commissies op een rij, met het moment in de video.</span></button>'"""),
     ("Een zoekmachine voor wat er letterlijk in de Rotterdamse gemeenteraad is gezegd, bedoeld voor","Een zoekmachine voor wat er in de commissies van de Rotterdamse gemeenteraad is gezegd, bedoeld voor"),
     ("de woordelijke notulen van '+nf(T.verg||0)+' raadsvergaderingen sinds 2018 (pdf), de agenda’s met sprekerstijdlijn, en de automatische ondertiteling van de uitzendingen.","de agenda’s met sprekerstijdlijn en de automatische ondertiteling van '+nf(T.auto||0)+' commissievergaderingen. Van commissies bestaan geen woordelijke notulen; ondertiteling is er vanaf 2022."),
     ("De notulen zijn automatisch opgeknipt per spreekbeurt en gekoppeld aan spreker, partij, rol en agendapunt. Motieteksten en stemuitslagen zijn apart gezet. Voor 2022–2026 zijn de notulen naast de ondertiteling gelegd om bij elke spreekbeurt het moment in de video te vinden.","De ondertiteling is met de sprekerstijdlijn van de vergadering opgeknipt per spreekbeurt: de tijdlijn zegt wie wanneer aan het woord was, de ondertiteling wat er gezegd is."),
     ("controleer een citaat in de bron (pdf met paginanummer, of de video) voordat je het gebruikt. Tekst met het label ‘automatische ondertiteling’ is geen officieel verslag en bevat herkenningsfouten. Commissievergaderingen zitten er nog niet in.","alle tekst hier is automatische ondertiteling en bevat herkenningsfouten, ook in namen en cijfers. Het is geen officieel verslag: controleer een citaat altijd in de video. Het begin van een spreekbeurt kan een paar seconden verschuiven, waardoor een zin bij de vorige spreker terechtkomt."),
     ('<a data-theme="spreidingswet">spreidingswet</a>','<a data-theme="technische vragen">technische vragen</a>'),
     ("' · nog geen notulen: tekst is automatische ondertiteling van de uitzending'","' · automatische ondertiteling van de uitzending'"),
    ]
    for a,b in R:
        assert a in t, a[:60]
        t=t.replace(a,b)
    return t
