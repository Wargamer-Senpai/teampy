#!/bin/bash
#
#
# this is a script to watch over the bot, the bot for some reason crashes/freezes inside a container.
# 
BOT_PID=0


# function kill_container(){
#   exit 69
# }

function start_bot(){
  if [[ $BOT_PID -ne 0 ]]; then
    kill -9 $BOT_PID
  fi

  /usr/bin/python3 /opt/teampy/main.py &
  BOT_PID=$!
  /bin/sleep 60
}


if [[ $CONTAINER_BOOL == "True" ]]; then
  COUNT_RAM_FAILS=0
  echo "Started Container $(date)"
  start_bot

  # CHECK RAM
  while true; do
    # check change timestamp
    TIMESTAMP_FILE=$(stat check_container | grep Change | awk -F: '{print $4}' | awk -F. '{print $1}')
    TIMESTAMP_DATE=$(date | awk -F: '{print $3}' | awk '{print $1}')
    TIMESTAMP_DIFF=$((10#$TIMESTAMP_DATE-10#$TIMESTAMP_FILE))

    # if time difrence is greater then 10 seconds kill, #0 casts the number to be an INT not Octal
    if [[ ${TIMESTAMP_DIFF#0} -gt 10 ]]; then
      echo '[ERROR] Bot didnt touched file, killing the bot *bonk*'
      start_bot
    fi

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
      echo '[ERROR] Bot didnt used ram for a long time, killing the bot *bonk*'
      start_bot
    fi
    if [[ "$RAM_USAGE" == "" || "$RAM_USAGE" == " " || -z "$RAM_USAGE" ]]; then
      echo '[ERROR] Where is the PID, killing the bot *bonk*'
      start_bot
    fi

    /bin/sleep 1
  done
fi