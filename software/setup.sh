#!/usr/bin/env bash

# This is the script meant for setting up a new RPi
app_dir="$HOME/MSD_P18538" # The directory where the app is located
env="$app_dir/software/environment.sh" # The environment file
backend_env="$app_dir/software/backend/.env" # The backend environment file
log_file="$HOME/setup.log" # The log file

# Ask user for api key if it doesn't exist
source $HOME/.bashrc | tee -a $log_file
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Enter your OpenAI API key:"
  read -r OPENAI_API_KEY
fi

# Update machine and setup environment
sudo apt update | tee -a $log_file && sudo apt upgrade -y | tee -a $log_file
# Install dependencies for project
sudo apt install tmux git -y | tee -a $log_file

# Clone the repository if it doesn't exist
if [ ! -d "$app_dir" ]; then
  repo="https://github.com/BrianMonclus/MSD_P18538.git" # The git repository
  git clone $repo $app_dir | tee -a $log_file
fi
if [ -z "$(grep 'source $env' $HOME/.bashrc)" ]; then
  echo "source $env" >> $HOME/.bashrc
fi
if [ -z "$(grep 'OPENAI_API_KEY' $backend_env)" ]; then
  echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> $backend_env
fi
echo ".bashrc setup complete." | tee -a $log_file

# Setup backend environment
# =============================================================================

# Install dependencies for building python from source:
# https://devguide.python.org/getting-started/setup-building/#build-dependencies
sudo apt install build-essential gdb lcov pkg-config \
  libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
  libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev lzma lzma-dev \
  tk-dev uuid-dev zlib1g-dev -y | tee -a $log_file

# Install dependencies for the backend
sudo apt install portaudio19-dev -y | tee -a $log_file # Audio input/output
sudo apt install ffmpeg -y | tee -a $log_file          # Audio decoding
echo "Backend dependencies installed." | tee -a $log_file

# Install python environment manager
if [ ! -d "$HOME/.pyenv" ]; then
  sudo curl https://pyenv.run | bash | tee -a $log_file
  echo "Installed python 3.12." | tee -a $log_file
fi
source $env
echo "Installed pyenv." | tee -a $log_file

# Install python 3.12 and set it as the active version
if [ -z "$(pyenv versions | grep 3.12)" ]; then
  pyenv install 3.12 | tee -a $log_file
fi
pyenv local 3.12 | tee -a $log_file # Set python 3.12 as local version

# Setup python environment
cd $app_dir
req_file="$app_dir/software/backend/requirements.txt" # The requirements file
python -m venv .venv | tee -a $log_file      # Create virtual environment
source .venv/bin/activate                    # Activate virtual environment
pip install -r $req_file | tee -a $log_file  # Install dependencies
deactivate                                   # Deactivate virtual environment
echo "Python environment setup complete." | tee -a $log_file

# Setup .net environment
# =============================================================================

# Install latest version of .net (8.0.101)
# more info: https://learn.microsoft.com/en-us/dotnet/iot/deployment
cd $HOME
sudo curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version latest | tee -a $log_file
source $env | tee -a $log_file
sudo rm -f /usr/local/bin/dotnet | tee -a $log_file
sudo ln -s $DOTNET_ROOT/dotnet /usr/local/bin/dotnet | tee -a $log_file
echo ".net environment setup complete." | tee -a $log_file

# Setup AdHoc network
# =============================================================================

# For adhoc network ensure we have dhcp server downloaded and configured to
# automatically handle IP hosting
sudo apt install isc-dhcp-server -y | tee -a $log_file
dhcpd_conf="$app_dir/software/backend/app/services/network/dhcpd.conf"
sudo cp $dhcpd_conf /etc/dhcp/dhcpd.conf
echo "AdHoc network setup complete." | tee -a $log_file

# Setup HTTPS certificates
# =============================================================================

# Install mkcert for generating certificates
sudo curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/arm64"
sudo chmod +x mkcert-v*-linux-arm64
sudo cp mkcert-v*-linux-arm64 /usr/local/bin/mkcert
sudo rm mkcert-v*-linux-arm64
sudo mkcert -install | tee -a $log_file
echo "mkcert installed." | tee -a $log_file

# Generate certificates
cert_dir="$app_dir/software/backend/data" # The directory of certificates
cd $cert_dir && mkcert -cert-file certificate.pem -key-file private.key \
  'localhost' '*.local' '*.student.rit.edu' | tee -a $log_file
sys_cert_path="/usr/local/share/ca-certificates/MSD_P18538.crt"
root_cert="$(mkcert -CAROOT)/rootCA.pem"
sudo cp certificate.pem $sys_cert_path
sudo update-ca-certificates | tee -a $log_file
sudo openssl verify -CAfile $root_cert $sys_cert_path | tee -a $log_file
echo "Certificates generated." | tee -a $log_file

# Setup services
# =============================================================================

sudo chmod +x $app_dir/software/startup.sh | tee -a $log_file
service_file="$app_dir/software/software.service" # The service file

# Install services
sudo cp $service_file /etc/systemd/system/software.service | tee -a $log_file
sudo systemctl daemon-reload | tee -a $log_file # Reload service files
sudo systemctl enable software.service | tee -a $log_file # Start service
sudo systemctl start software.service | tee -a $log_file # Start the service
sudo systemctl status software.service | tee -a $log_file # Check status
echo "Services setup complete." | tee -a $log_file

sudo reboot # Restart the system to apply some changes
