# Raadzoeker: werkt de site bij op de NAS (Synology DS224+, x86-64). Zie ontwerp/fase6-instructies.md.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git openssh-client ca-certificates curl tzdata fonts-liberation && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL -o /usr/local/bin/supercronic https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 \
 && chmod +x /usr/local/bin/supercronic
RUN pip install --no-cache-dir pymupdf beautifulsoup4 lxml numpy zstandard pillow
ENV TZ=Europe/Amsterdam PYTHONUTF8=1 PYTHONUNBUFFERED=1
COPY crontab /etc/raadzoeker.cron
COPY start.sh /usr/local/bin/start.sh
CMD ["sh","/usr/local/bin/start.sh"]
