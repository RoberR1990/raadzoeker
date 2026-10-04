-- Raadzoeker, Cloudflare D1 (binding 'DB'). Eenmalig uitvoeren in de D1-console.
-- ideeen: de ideeënlijst; status idee | gepland | gebouwd. Een stem op een gebouwd idee telt niet meer mee voor de limiet van 3.
-- stemmen: één rij per persoon per idee; de persoon is een SHA-256-hash van het e-mailadres uit Cloudflare Access (geen adres opgeslagen).
-- zoeklog: anonieme zoekopdrachten (geen persoon, alleen de dag), vooral om te zien wat niets oplevert.
CREATE TABLE IF NOT EXISTS ideeen (id INTEGER PRIMARY KEY, titel TEXT NOT NULL, toelichting TEXT, status TEXT NOT NULL DEFAULT 'idee', volgorde INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS stemmen (idee_id INTEGER NOT NULL, gebruiker TEXT NOT NULL, moment TEXT NOT NULL, PRIMARY KEY (idee_id, gebruiker));
CREATE TABLE IF NOT EXISTS zoeklog (id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT NOT NULL, n INTEGER, pagina TEXT, dag TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS zoeklog_dag ON zoeklog(dag);

INSERT OR IGNORE INTO ideeen (id, titel, toelichting, status, volgorde) VALUES
 (1, 'Meldingen bij nieuws in jouw dossier', 'Een mail of Teams-bericht als er een nieuwe motie, toezegging of brief binnenkomt over een onderwerp of wijk die je volgt.', 'idee', 1),
 (2, 'Elke dag bijgewerkt', 'Nu wordt de site met de hand bijgewerkt. Elke nacht automatisch ophalen, uitlezen en indexeren, zodat zoeken altijd actueel is.', 'gepland', 2),
 (3, 'Thema''s als derde ingang', 'Naast domeinen en gebieden ook thema''s die overal doorheen lopen, zoals AI en algoritmes, participatie of kansengelijkheid.', 'idee', 3),
 (4, 'Samenvattingen voor alle gebieden', 'Nu hebben 8 van de 14 gebieden een AI-samenvatting. De andere 6: Hillegersberg-Schiebroek, Hoek van Holland, Hoogvliet, Overschie, Pernis en Rozenburg.', 'gepland', 4),
 (5, 'Commissievergaderingen zonder ondertiteling', 'Van 61 commissievergaderingen is wel video maar geen ondertiteling. Met spraakherkenning zijn ook die doorzoekbaar.', 'idee', 5),
 (6, 'Meer bronnen: Tweede Kamer, provincie en MRDH', 'Zien wat er landelijk en regionaal over hetzelfde dossier is besloten, zoals over openbaar vervoer en wonen.', 'idee', 6),
 (7, 'Andere gemeenten', 'Dezelfde opzet voor Amsterdam, Den Haag en Utrecht via Open Raadsinformatie, zodat je kunt vergelijken.', 'idee', 7),
 (8, 'Interne bronnen', 'Koppelen met interne documenten van de gemeente. Dat verandert het karakter: dan is het geen open-dataproduct meer en moet het intern draaien.', 'idee', 8),
 (9, 'Elk onderwerp als voorbeeldpagina', 'De opbouw van Parkeren (komt eraan, gezegd, besloten, beloofd, gedaan, in de stad) voor alle onderwerpen.', 'idee', 9),
 (10, 'Persoonlijke volglijst', 'Onderwerpen, wijken en moties bewaren in een eigen lijst, met wat er sinds je laatste bezoek is veranderd.', 'idee', 10),
 (11, 'Briefing direct in Teams delen', 'De briefing als kaart in een Teams-kanaal plaatsen, met link naar de bron.', 'idee', 11);
