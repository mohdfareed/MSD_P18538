#!/usr/bin/env bash

# This is the script primarily meant for setting up a new RPi
# It sets up the environment for the backend (python) and frontend (.net)
app_dir="$HOME/MSD_P18538" # The directory where the app is located
env="$app_dir/software/environment.sh"

# Ask user for info
echo "Enter your OpenAI API key:"
read -r OPENAI_API_KEY

# Update machine and setup environment
sudo apt update && sudo apt upgrade -y
# Install dependencies for project
sudo apt install tmux git -y

# Clone the repository if it doesn't exist
if [ ! -d "$app_dir" ]; then
  git clone https://github.com/BrianMonclus/MSD_P18538.git $app_dir
fi
echo "source $env" >> ~/.bashrc
echo "export OPEN_AI_API_KEY=$OPENAI_API_KEY" >> ~/.bashrc

# Setup backend environment
# =============================================================================

# Install dependencies for building python from source:
# https://devguide.python.org/getting-started/setup-building/#build-dependencies
sudo apt install build-essential gdb lcov pkg-config portaudio19-dev \
  libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
  libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev lzma lzma-dev \
  tk-dev uuid-dev zlib1g-dev -y

# Install dependencies for the backend
sudo apt install portaudio19-dev -y # Audio input/output
sudo apt install ffmpeg -y          # Audio decoding

# Install python environment manager
sudo rm -rf ~/.pyenv
sudo curl https://pyenv.run | bash
source $env
cd $app_dir

# Install python 3.12 and set it as the active version
req_file="$app_dir/software/backend/requirements.txt"
pyenv install 3.12            # Install python 3.12
pyenv local 3.12              # Set python 3.12 as the local version
python -m venv .venv          # Create virtual environment
source .venv/bin/activate     # Activate virtual environment
pip install -r $req_file      # Install dependencies

# Validate python version
py_ver=$(python --version | awk '{print $2}' | awk -F. '{print $1 "." $2}')
if [ "$py_ver" != "3.12" ]; then
  echo "Python version is not 3.12"
  exit 1
fi
deactivate # Deactivate virtual environment after validation

# Setup .net environment
# =============================================================================

# Install latest version of .net (8.0.101)
# more info: https://learn.microsoft.com/en-us/dotnet/iot/deployment
cd ~
sudo curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version latest
source $env
sudo rm -f /usr/local/bin/dotnet
sudo ln -s $DOTNET_ROOT/dotnet /usr/local/bin/dotnet

# Setup AdHoc network
# =============================================================================

# For adhoc network ensure we have dhcp server downloaded and configured to
# automatically handle IP hosting
sudo apt install isc-dhcp-server -y
dhcpd_conf="$app_dir/software/backend/app/services/network/dhcpd.conf"
sudo cp $dhcpd_conf /etc/dhcp/dhcpd.conf

# Setup HTTPS certificates
# =============================================================================

# Install mkcert for generating certificates
sudo curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
sudo chmod +x mkcert-v*-linux-amd64
sudo cp mkcert-v*-linux-amd64 /usr/local/bin/mkcert
sudo rm mkcert-v*-linux-amd64
sudo mkcert -install

# Generate certificates for backend
cd $app_dir/software/certificates
sudo mkcert -cert-file certificate.pem -key-file private.key \
  'localhost' '*.local' '*.student.rit.edu'
sudo cp cert.pem /usr/local/share/ca-certificates/MSD_P18538_frontend.crt
sudo update-ca-certificates
sudo openssl verify /usr/local/share/ca-certificates/MSD_P18538_frontend.crt

# Generate certificates for frontend https
sudo dotnet dev-certs --clean
sudo dotnet dev-certs https --format pem \
  --export-path /usr/local/share/ca-certificates/MSD_P18538_frontend.crt
sudo update-ca-certificates
sudo openssl verify /usr/local/share/ca-certificates/MSD_P18538_frontend.crt

# Setup services
# =============================================================================

# Install services
cd $app_dir/software # Change to dir of this script again
sudo cp ./software.service /etc/systemd/user/software.service

# Refresh systemd (reload service files)
sudo systemctl --user daemon-reload
sudo systemctl --global daemon-reload

# Enable services to start on boot
sudo systemctl --global enable software.service
sudo reboot # Restart the system to apply some changes
