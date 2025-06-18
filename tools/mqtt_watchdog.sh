#!/bin/sh

CONTAINER_NAME="mqtt-ingest"
DB_CONTAINER="repo-db-1"
MAX_LAG_SECONDS=120

check_container_running() {
  docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null | grep true >/dev/null
}

check_db_lag_ok() {
  LAG=$(docker exec "$DB_CONTAINER" psql -U postgres -d hslbussit -t -c "SELECT EXTRACT(EPOCH FROM NOW() - MAX(tst)) FROM mqtt_hfp;" | tr -d '[:space:]')
  [ "$LAG" != "" ] && [ "$(printf '%.0f' "$LAG")" -lt "$MAX_LAG_SECONDS" ]
}

restart_container() {
  echo "[watchdog] Restarting $CONTAINER_NAME due to failure"
  docker restart "$CONTAINER_NAME"
}

log_status() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [watchdog] $1"
}

if ! check_container_running; then
  log_status "$CONTAINER_NAME is not running"
  restart_container
  exit 1
fi

if ! check_db_lag_ok; then
  log_status "DB insert lag too high"
  restart_container
  exit 2
fi

log_status "All OK"
exit 0
