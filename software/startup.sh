#!/usr/bin/env bash

# cd to path of this script
cd "$(dirname "$0")"

SESSION_NAME="software"                 # Name of the tmux session
BACKEND_SCRIPT="./backend/startup.py"   # Backend startup script
FRONTEND_SCRIPT="./frontend/startup.py" # Frontend startup script
VENV="source ../.venv/bin/activate"     # Activate virtual environment

# Check if --debug or -d flag is passed
if [ "$1" == "--debug" ] || [ "$1" == "-d" ]; then
  BACKEND_SCRIPT="./backend/startup.py --debug"
  FRONTEND_SCRIPT="./frontend/startup.py --debug"
fi

tmux kill-session -t $SESSION_NAME 2> /dev/null # Delete previous session
tmux new-session -d -s $SESSION_NAME            # Create a new session
tmux rename-window -t $SESSION_NAME 'backend'   # Rename the backend window
tmux new-window -t $SESSION_NAME -n 'frontend'  # Create frontend window

# Load the shell environment
tmux send-keys -t $SESSION_NAME "source ./environment.sh" C-m
tmux send-keys -t $SESSION_NAME:1 "source ./environment.sh" C-m

tmux send-keys -t $SESSION_NAME "$VENV" C-m              # Activate venv
tmux send-keys -t $SESSION_NAME "$BACKEND_SCRIPT" C-m    # Start backend
tmux send-keys -t $SESSION_NAME:1 "$FRONTEND_SCRIPT" C-m # Start frontend
tmux attach -t $SESSION_NAME                             # Attach to session
