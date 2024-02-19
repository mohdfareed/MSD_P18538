# This is the script primarally meant to RPi
# todo:
#  - Possibly automate more in the future, i.e. run venv script
#  - Eventally might need to ensure that certain directories get created
#

# Ensure root privileges 
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Update all packages
apt update && apt upgrade

# For adhoc network ensure we have dhcp server downloaded and configured to automaticly handle Ip hosting
apt install isc-dhcp-server
cp ~/MSD_P18538/software/backend/app/services/network/dhcpd.conf /etc/dhcp/dhcpd.conf

# Install Python 3.12.1 and set as the primary version 
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev  libsqlite3-dev

cd ~
wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz

tar -xzvf Python-3.12.1.tgz 
cd Python-3.12.1/
./configure --enable-optimizations
make altinstall

rm /usr/bin/python
ln -s /usr/local/bin/python3.12 /usr/bin/python

cd /tmp/
rm -rf rm -rf Python-3.12.1.tgz Python-3.12.1/

# Install latest version of .net (8.0.101)
# more info: https://learn.microsoft.com/en-us/dotnet/iot/deployment
cd ~
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version latest

echo 'export DOTNET_ROOT=$HOME/.dotnet' >> ~/.bashrc
echo 'export PATH=$PATH:$HOME/.dotnet' >> ~/.bashrc
source ~/.bashrc # Warning: This line failed, might have to manually run it

# Check the installs
python -VV
dotnet --version
