#!/usr/bin/env bash

cd $HOME/MSD_P18538/software/backend
SESSION_NAME="MSD_P18538"  # name of the tmux session
SCRIPT="./startup.py" # startup script
chmod +x $SCRIPT

# create a new tmux session and run the startup script
tmux kill-session -t $SESSION_NAME 2> /dev/null # delete previous session
tmux new-session -d -s $SESSION_NAME            # create a new session
tmux send-keys -t $SESSION_NAME "$SCRIPT" C-m   # start app

# open web browser to the frontend
if ! command -v chromium-browser &> /dev/null; then
  echo "chromium-browser not found"
  exit 1
fi
ip=$(hostname -I | awk '{print $1}')
chromium-browser --app=https://$ip 2> /dev/null &
