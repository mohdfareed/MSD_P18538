#!/usr/bin/env bash

work_dir="$HOME/msd-p18538"
SESSION_NAME="MSD-P18538"  # name of the tmux session
SCRIPT="$work_dir/software/backend/startup.py" # startup script
PYTHON="$work_dir/.venv/bin/python" # virtual environment
chmod +x $SCRIPT

# create a new tmux session and run the startup script
tmux kill-session -t $SESSION_NAME 2> /dev/null # delete previous session
tmux new-session -d -s $SESSION_NAME            # create a new session
tmux send-keys -t $SESSION_NAME "sudo $PYTHON $SCRIPT" C-m   # start app

if command -v chromium-browser &> /dev/null; then
  ip=$(hostname -I | awk '{print $1}')
  chromium-browser --app="https://$ip" 2> /dev/null &
else
  echo "chromium-browser not found, cannot open UI."
fi
