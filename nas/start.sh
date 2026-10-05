#!/bin/sh
# Eerste start: de repository ophalen met de deploy-sleutel (ssh/id_ed25519, publieke sleutel staat als 'deploy key' met schrijfrechten op GitHub).
set -e
mkdir -p /root/.ssh && cp /ssh/id_ed25519 /root/.ssh/id_ed25519 && chmod 600 /root/.ssh/id_ed25519
ssh-keyscan github.com >> /root/.ssh/known_hosts 2>/dev/null
if [ ! -d /repo/.git ]; then git clone git@github.com:RoberR1990/raadzoeker.git /repo; fi
git -C /repo config user.name "Raadzoeker NAS"; git -C /repo config user.email "raadzoeker-nas@users.noreply.github.com"
echo "raadzoeker-bijwerker gestart $(date)"
exec supercronic -passthrough-logs /etc/raadzoeker.cron
