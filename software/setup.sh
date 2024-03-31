# This is the script primarily meant for setting up a new RPi
# It sets up the environment for the backend (python) and frontend (.net)

app_dir='~/MSD_P18538' # The directory where the app is located

# Ensure root privileges
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Clone the repository if it doesn't exist
if [ ! -d "$app_dir" ]; then
  git clone https://github.com/BrianMonclus/MSD_P18538.git $app_dir

# Update packages
sudo apt update && sudo apt upgrade -y
# Setup .bashrc
echo "source $app_dir/software/bashrc" >> ~/.bashrc

# For adhoc network ensure we have dhcp server downloaded and configured to automaticly handle Ip hosting
sudo apt install isc-dhcp-server
sudo cp ~/MSD_P18538/software/backend/app/services/network/dhcpd.conf /etc/dhcp/dhcpd.conf

# Install dependencies for building python from source:
# https://devguide.python.org/getting-started/setup-building/#build-dependencies
sudo apt install build-essential gdb lcov pkg-config portaudio19-dev \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev ffmpeg -y
# REVIEW: unfortunately, pre-built python versions are only available on ubuntu
# Added packages: portaudio19-dev (for pyaudio)
#                 ffmpeg (for audio decoding)

# Setup python environment
cd $app_dir/software                    # Change to dir of this script
curl https://pyenv.run | bash           # Install env manager
source ~/.bashrc || true                # Reload bashrc
pyenv install 3.12                      # Install python 3.12
pyenv virtualenv 3.12 backend           # Create virtual environment
pyenv activate backend                  # Activate virtual environment
pip install -r backend/requirements.txt # Install dependencies

# Install latest version of .net (8.0.101)
# more info: https://learn.microsoft.com/en-us/dotnet/iot/deployment
cd ~
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version latest
source ~/.bashrc || true

# Check the installations and bashrc validity
python -VV
dotnet --version
source ~/.bashrc

# Install services
cd $app_dir/software # Change to dir of this script again
sudo cp ./backend.service /etc/systemd/user/backend.service
sudo cp ./frontend.service /etc/systemd/user/frontend.service

# Refresh systemd (reload service files)
systemctl --user daemon-reload
sudo systemctl --global daemon-reload

# Enable services to start on boot
sudo systemctl --global enable backend
sudo systemctl --global enable frontend
sudo reboot # Restart the system to apply some changes
