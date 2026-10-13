#!/bin/sh
# Eerste start: de repository ophalen met de deploy-sleutel (ssh/id_ed25519, publieke sleutel staat als 'deploy key' met schrijfrechten op GitHub).
# Codeslot: cron start niet bijwerken.sh uit de repo, maar /usr/local/bin/codeslot.sh (hieronder, buiten de repo). Dat draait alleen
# code (src/, nas/) die precies zo met Roberts sleutel is ondertekend (commit of tag nas-ok-*). Vertrouwde sleutels: /ssh/allowed_signers.
set -e
mkdir -p /root/.ssh && cp /ssh/id_ed25519 /root/.ssh/id_ed25519 && chmod 600 /root/.ssh/id_ed25519
# vaste sleutel van GitHub (gepubliceerd op docs.github.com), niet blind ophalen
echo "github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl" > /root/.ssh/known_hosts
git config --global --add safe.directory /repo
if [ ! -d /repo/.git ]; then git clone git@github.com:RoberR1990/raadzoeker.git /repo; fi
git -C /repo config user.name "Raadzoeker NAS"; git -C /repo config user.email "raadzoeker-nas@users.noreply.github.com"
git -C /repo config gpg.ssh.allowedSignersFile /ssh/allowed_signers

cat > /usr/local/bin/codeslot.sh <<'SLOT'
#!/bin/sh
MODUS=${1:-nacht}
cd /repo || exit 1
blok(){
  printf '{"laatste":"%s","modus":"%s","ok":false,"stap":"codeslot","log":"%s"}\n' "$(date -Iseconds)" "$MODUS" "$1" > /werk/status.json
  [ -n "$NTFY" ] && curl -s -d "Raadzoeker: run gestopt door codeslot ($1). Keur de code goed met nas/keur.sh." "https://ntfy.sh/$NTFY" >/dev/null
  echo "codeslot: $1"; exit 1; }
[ -s /ssh/allowed_signers ] || blok "geen /ssh/allowed_signers"
git fetch -q --force --tags origin || blok "git fetch mislukt"
DOEL=$(git rev-parse origin/main)
boom(){ echo "$(git rev-parse -q --verify "$1:src") $(git rev-parse -q --verify "$1:nas")"; }
NU=$(boom "$DOEL"); OK=""
# een ondertekende commit met precies dezelfde src/ en nas/ (nieuwste eerst), anders een ondertekende tag nas-ok-*
for c in $(git log -n 300 --format=%H "$DOEL"); do
  [ "$(boom "$c")" = "$NU" ] && git verify-commit "$c" >/dev/null 2>&1 && { OK=$c; break; }
done
if [ -z "$OK" ]; then for t in $(git tag -l 'nas-ok-*' --sort=-creatordate | head -n 30); do
  [ "$(boom "$t^{commit}")" = "$NU" ] && git verify-tag "$t" >/dev/null 2>&1 && { OK=$t; break; }
done; fi
[ -n "$OK" ] || blok "code op main ${DOEL%"${DOEL#???????}"} is niet ondertekend"
# de goedgekeurde versie van bijwerken.sh los draaien (de repo verandert tijdens de run)
git show "$DOEL:nas/bijwerken.sh" > /tmp/bijwerken.sh
RZ_CODE=$DOEL exec sh /tmp/bijwerken.sh "$MODUS"
SLOT
chmod 755 /usr/local/bin/codeslot.sh
cat > /etc/raadzoeker.cron <<'CRON'
30 2 * * *        sh /usr/local/bin/codeslot.sh nacht
15 9-21/3 * * 1-5 sh /usr/local/bin/codeslot.sh overdag
CRON

echo "raadzoeker-bijwerker gestart $(date)"
exec /usr/local/bin/supercronic -no-reap -passthrough-logs /etc/raadzoeker.cron
