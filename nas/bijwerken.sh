#!/bin/sh
# Werkt de raadzoeker bij en zet de site online (git push -> Cloudflare Pages).
#   nacht:   iBabs (nieuwe stukken + open moties/toezeggingen verversen), vragen met antwoord, raadsvoorstellen, Gemeenteblad,
#            zoekindex, domein- en gebiedslabels, dossiers, voorbeelddossiers, Lab
#   overdag: alleen iBabs-lijsten en nieuwe moties, toezeggingen en brieven, en de pagina's die daarvan afhangen
# Nog niet automatisch (zie ontwerp/fase6-instructies.md): nieuwe debatten (notulen/ondertiteling), wijkraadvergaderingen, AI-samenvattingen.
# Logboek per run met wijzigingen: docs/data/logboek.json (src/logboek.py, pagina ontwerp/nieuw.html).
# Status van elke run: /werk/status.json en in de site docs/data/status.json. Faalt een stap, dan wordt er niets gepusht.
MODUS=${1:-nacht}
cd /repo || exit 1
export RZ_WERK=/werk RZ_BRON=/werk RZ_STAND=$(date +%F) RZ_VERS=1 PYTHONUTF8=1
LOG=/werk/logs/$(date +%F_%H%M)_$MODUS.log; mkdir -p /werk/logs
STAP=""; STAPPEN=""
stap(){ STAP="$1"; shift; echo "== $STAP $(date +%T)" >>"$LOG"; "$@" >>"$LOG" 2>&1 || { fout; exit 1; }; STAPPEN="$STAPPEN\"$STAP\","; }
fout(){
  printf '{"laatste":"%s","modus":"%s","ok":false,"stap":"%s","log":"%s"}\n' "$(date -Iseconds)" "$MODUS" "$STAP" "$LOG" > /werk/status.json
  [ -n "$NTFY" ] && curl -s -d "Raadzoeker: $MODUS mislukt bij '$STAP'. Zie $LOG" "https://ntfy.sh/$NTFY" >/dev/null
  git -C /repo checkout -- docs >/dev/null 2>&1
}
# altijd beginnen vanaf de laatste versie op GitHub; een eerdere, niet-gepushte run wordt weggegooid (alle data wordt opnieuw gemaakt)
# eerst een eventueel blijven hangende rebase of merge opruimen (die liet elke volgende run mislukken bij 'git push')
git rebase --abort >/dev/null 2>&1; git merge --abort >/dev/null 2>&1; rm -rf .git/rebase-merge .git/rebase-apply .git/index.lock
stap "git fetch" git fetch -q origin
stap "git reset" git checkout -q -f -B main origin/main
# ontbrekende onderdelen zelf bijinstalleren (zo hoeft de container niet opnieuw gebouwd te worden na een wijziging in de Dockerfile)
python -c "import PIL, zstandard" 2>/dev/null || pip install -q --no-cache-dir pillow zstandard >>"$LOG" 2>&1
[ -f /usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf ] || { apt-get update -qq && apt-get install -y -qq --no-install-recommends fonts-liberation; } >>"$LOG" 2>&1
# logboek 'Wat is er nieuw': stand vóór de run vastleggen (mag mislukken)
python src/logboek.py voor >>"$LOG" 2>&1 || echo "logboek voor mislukt" >>"$LOG"
stap "iBabs-lijsten" python src/ibabs_lijsten.py
if [ "$MODUS" = "nacht" ]; then
  stap "iBabs-stukken" python src/ibabs_items.py toezeggingen moties amendementen raadsvoorstellen initiatiefvoorstellen brieven wijkraadadviezen --ververs-open --minuten 90
  stap "vragen" python src/sv_qa.py --minuten 30
  stap "raadsvoorstellen" python src/bijlagen.py rv --minuten 20
  stap "Gemeenteblad" python src/bekendmakingen.py --recent
  stap "iBabs naar site" python src/ibabs_emit.py
  stap "zoekindex stukken" python src/teksten.py
  stap "domeinen" python src/domeinen.py
  stap "gebieden" python src/gebieden.py
  stap "dossiers" python src/ontwerp_data.py
  stap "RDW parkeren" python src/parkeren_rdw.py
else
  stap "iBabs-stukken" python src/ibabs_items.py toezeggingen moties brieven --minuten 20
  stap "iBabs naar site" python src/ibabs_emit.py
  stap "zoekindex stukken" python src/teksten.py
fi
# Verkenner (kennisgraaf, ca. 35 min): wekelijks, in de nacht van zaterdag op zondag
if [ "$MODUS" = "nacht" ] && [ "$(date +%u)" = "7" ]; then stap "verkenner" python src/verkenner.py; fi
stap "dossierbestanden" python src/dossier_data.py
stap "voorbeelddossiers" python src/showcase.py
stap "deelkaarten" python src/deelkaart.py   # leest dossier_data en showcase; lettertype Liberation Sans (of RZ_FONTS)
stap "Lab" python src/lab_data.py
python src/tracker.py >>"$LOG" 2>&1 || echo "tracker mislukt" >>"$LOG"
stap "vergaderingen koppelen" python src/verg_koppel.py
stap "vooruitblik" python src/vooruit.py
stap "volgen" python src/volg_data.py
RZ_MODUS=$MODUS python src/logboek.py na >>"$LOG" 2>&1 || echo "logboek na mislukt" >>"$LOG"
printf '{"laatste":"%s","modus":"%s","ok":true,"stand":"%s"}\n' "$(date -Iseconds)" "$MODUS" "$RZ_STAND" | tee /werk/status.json > docs/data/status.json
git add -A docs
if git diff --cached --quiet; then echo "niets veranderd" >>"$LOG"; exit 0; fi
stap "git commit" git commit -q -m "Automatisch bijgewerkt ($MODUS, $(date '+%d-%m-%Y %H:%M'))"
# er kan intussen iets anders gepusht zijn: tot 3 keer bijwerken en opnieuw proberen
# Bij een conflict wint de verse versie van deze run (-X theirs; alle data hier wordt opnieuw gemaakt). Mislukt een poging, dan altijd de rebase afbreken,
# zodat de repository nooit half in een rebase blijft staan.
duw(){ for i in 1 2 3; do
    git fetch -q origin && git rebase -q -X theirs origin/main && git push -q origin HEAD:main && return 0
    git rebase --abort >/dev/null 2>&1; sleep 20
  done; return 1; }
stap "git push" duw
# meldingen voor wie onderwerpen volgt (mag mislukken zonder de run te laten falen)
python src/push_stuur.py >>"$LOG" 2>&1 || echo "push mislukt" >>"$LOG"
find /werk/logs -name '*.log' -mtime +30 -delete
