#!/usr/bin/env bash

# cd to path of this script
cd "$(dirname "$0")"

SESSION_NAME="software"             # name of the tmux session
SCRIPT="./backend/startup.py"  # startup script
VENV="source ../.venv/bin/activate" # activate virtual environment

tmux kill-session -t $SESSION_NAME 2> /dev/null # delete previous session
tmux new-session -d -s $SESSION_NAME            # create a new session

# Load the shell environment
tmux send-keys -t $SESSION_NAME "source ./environment.sh" C-m # Load env
tmux send-keys -t $SESSION_NAME "$VENV" C-m                   # activate venv
tmux send-keys -t $SESSION_NAME "$SCRIPT" C-m                 # start app

if ! command -v chromium-browser &> /dev/null; then
  echo "chromium-browser not found"
  exit 0
fi

# Open web browser to the frontend
ip=$(hostname -I | awk '{print $1}')
chromium-browser --app=https://$ip 2> /dev/null &
