#!/bin/bash
# Attend que le serveur Flask soit prêt avant d'ouvrir Chromium

MAX_WAIT=30
COUNT=0

until curl -s http://localhost:8080 > /dev/null 2>&1; do
  sleep 1
  COUNT=$((COUNT + 1))
  if [ $COUNT -ge $MAX_WAIT ]; then
    break
  fi
done

# Détecte le bon nom de l'exécutable Chromium
if command -v chromium &>/dev/null; then
  CHROMIUM_BIN="chromium"
elif command -v chromium-browser &>/dev/null; then
  CHROMIUM_BIN="chromium-browser"
else
  CHROMIUM_BIN="chromium"
fi

# --app= ouvre sans barre d'adresse ni onglets (mode application)
exec $CHROMIUM_BIN \
  --app=http://localhost:8080 \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-restore-session-state \
  --no-first-run \
  --disable-translate \
  --disable-features=TranslateUI \
  --window-size=800,480
