#!/bin/sh
# Werkt de raadzoeker bij en zet de site online (git push -> Cloudflare Pages).
#   nacht:   iBabs (nieuwe stukken + open moties/toezeggingen verversen), vragen met antwoord, raadsvoorstellen, Gemeenteblad,
#            zoekindex, domein- en gebiedslabels, dossiers, voorbeelddossiers, Lab
#   overdag: alleen iBabs-lijsten en nieuwe moties, toezeggingen en brieven, en de pagina's die daarvan afhangen
# Nog niet automatisch (zie ontwerp/fase6-instructies.md): nieuwe debatten (notulen/ondertiteling), wijkraadvergaderingen, AI-samenvattingen.
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
stap "git pull" git pull --ff-only
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
stap "dossierbestanden" python src/dossier_data.py
stap "voorbeelddossiers" python src/showcase.py
stap "Lab" python src/lab_data.py
printf '{"laatste":"%s","modus":"%s","ok":true,"stand":"%s"}\n' "$(date -Iseconds)" "$MODUS" "$RZ_STAND" | tee /werk/status.json > docs/data/status.json
git add -A docs
if git diff --cached --quiet; then echo "niets veranderd" >>"$LOG"; exit 0; fi
stap "git commit" git commit -q -m "Automatisch bijgewerkt ($MODUS, $(date '+%d-%m-%Y %H:%M'))"
stap "git push" git push -q
find /werk/logs -name '*.log' -mtime +30 -delete
