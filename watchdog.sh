#!/bin/bash

# Path to the file holding the current bot PID
PID_FILE="/opt/teampy/bot.pid"
# File the bot must touch to signal liveness
CHECK_FILE="/opt/teampy/check_container"
# Command to launch the bot
BOT_CMD="/usr/bin/python3 /opt/teampy/main.py"
# How long to sleep after starting the bot before monitoring
SLEEP_AFTER_START=60
# Monitoring interval in seconds
SLEEP_INTERVAL=1


# Read initial state
CONTAINER_BOOL="${CONTAINER_BOOL:-False}"
BOT_PID=0

# Write the current PID into $PID_FILE
function write_pid() {
  echo "$BOT_PID" > "$PID_FILE"
}

# Read the PID from $PID_FILE (or set to 0 if missing)
function read_pid() {
  if [[ -f "$PID_FILE" ]]; then
    BOT_PID=$(<"$PID_FILE")
  else
    BOT_PID=0
  fi
}

# (Re)start the bot, kill old PID if necessary,
# then write the new PID to PID_FILE
function start_bot() {
  if [[ $BOT_PID -ne 0 ]]; then
    kill -9 "$BOT_PID" 2>/dev/null || true
    wait "$BOT_PID" 2>/dev/null || true
  fi

  $BOT_CMD &
  BOT_PID=$!
  write_pid

  sleep $SLEEP_AFTER_START
}

# Main monitoring loop
function monitor_bot() {
  while true; do
    read_pid

    # If the process isn’t alive, check its exit code
    if ! kill -0 "$BOT_PID" 2>/dev/null; then
      wait "$BOT_PID" 2>/dev/null
      STATUS=$?
      if [[ $STATUS -eq 0 ]]; then
        echo "[INFO] Bot (PID $BOT_PID) exited cleanly. Exiting watchdog at $(date)"
        exit 0
      else
        echo "[ERROR] Bot (PID $BOT_PID) exited with status $STATUS. Restarting at $(date)"
        start_bot
        continue
      fi
    fi

    # Check that the bot has updated its checkpoint file recently
    if [[ -f "$CHECK_FILE" ]]; then
      FILE_TS=$(stat -c %Y "$CHECK_FILE")
      NOW_TS=$(date +%s)
      DIFF=$((NOW_TS - FILE_TS))
      if (( DIFF > 60 )); then
        echo "[ERROR] $CHECK_FILE untouched for $DIFF sec. Restarting at $(date)"
        start_bot
        continue
      fi
    else
      echo "[WARN] Check file $CHECK_FILE missing."
    fi

    sleep $SLEEP_INTERVAL
  done
}

# Entry point
if [[ "$CONTAINER_BOOL" == "True" ]]; then
  echo "Started watchdog at $(date)"
  start_bot
  monitor_bot
else
  echo "CONTAINER_BOOL is not True; exiting."
  exit 1
fi
