#!/bin/sh
# Codeslot: keur de code op main goed voor de NAS (draaien op Roberts pc, in Git Bash, vanuit D:\Raadzoeker).
# Nodig als code (src/ of nas/) is gewijzigd zonder ondertekening, bijvoorbeeld vanuit een cloudsessie.
# Toont wat er sinds de vorige goedkeuring in src/ en nas/ is veranderd en zet dan een ondertekende tag nas-ok-<datum>.
set -e
git fetch -q --tags origin
VORIG=$(git tag -l 'nas-ok-*' --sort=-creatordate | head -n 1)
if [ -n "$VORIG" ]; then echo "Gewijzigd sinds $VORIG:"; git diff --stat "$VORIG" origin/main -- src nas; fi
printf 'Deze code goedkeuren voor de NAS? (j/n) '; read a; [ "$a" = j ] || exit 1
T=nas-ok-$(date +%Y%m%d-%H%M)
git tag -s "$T" -m "Code goedgekeurd voor de NAS" origin/main && git push -q origin "$T" && echo "Goedgekeurd: $T"
