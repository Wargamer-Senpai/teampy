#!/bin/bash
if [[ $CONTAINER_BOOL == "True" ]]; then
  COUNT_RAM_FAILS=0
  KILL_CONTAINER=false

  /usr/bin/python3 /opt/teampy/main.py &
  STARTUP_CODE=$?
  if [[ $STARTUP_CODE -ne 0 ]]; then
    echo "[ERROR] Startup failed (Code $STARTUP_CODE)"
    exit 5
  fi

  # CHECK RAM
  while true; do
    # get ram usage
    # shellcheck disable=SC2062
    RAM_USAGE=$(top -n 1 | grep python[3] | awk '{print $8}') 

    # check if ram is 0% or empty, if true count it how many time
    if [[ "$RAM_USAGE" == "0%" ]]; then
      COUNT_RAM_FAILS=$((COUNT_RAM_FAILS+1))
    else
      COUNT_RAM_FAILS=0
    fi 
    if [[ $COUNT_RAM_FAILS -eq 50 ]]; then
      KILL_CONTAINER=true
    fi
    if [[ "$RAM_USAGE" == "" || "$RAM_USAGE" == " " || -z "$RAM_USAGE" ]]; then
      KILL_CONTAINER=true
    fi

    # kill the bot if it gues its to much
    if $KILL_CONTAINER; then
      exit 69
    fi

    /bin/sleep 1
  done
fi