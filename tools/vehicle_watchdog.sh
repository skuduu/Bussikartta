#!/bin/sh

log() {
  echo "$(date +'%F %T') [vehicle-watchdog] $1"
}

# Run SQL to determine lag in seconds
lag_sec=$(docker exec repo-db-1 psql -U postgres -d hslbussit -t -A -c \
"SELECT EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) FROM vehicle_positions;" 2>/dev/null)

# If result is empty or too large, trigger restart
if [ -z "$lag_sec" ]; then
  log "No data available, restarting vehicle-ingest"
  docker restart vehicle-ingest
elif [ "$(echo "$lag_sec > 90" | bc)" -eq 1 ]; then
  log "Insert lag too high (${lag_sec}s), restarting vehicle-ingest"
  docker restart vehicle-ingest
else
  log "OK – lag ${lag_sec}s"
fi
