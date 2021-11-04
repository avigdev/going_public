# NOTE that I don't run this script end to end but manually execute each line..
sudo apt-get -y install puppet-master
sudo puppet apply -v tools.pp
sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
mkdir progs
wget https://www.jetbrains.com/idea/download/download-thanks.html?platform=linux&code=IIC
mkdir code
cd code
git clone https://avigoz@bitbucket.org/roishillo/one-subtitle.git
# sudo puppet module install garethr-docker
# docker
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
# python is installed with puppet, but thereafter:
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
curl https://bootstrap.pypa.io/get-pip.py -o ~/progs/get-pip.py
python ~/progs/get-pip.py
sudo update-alternatives --install /usr/bin/pip pip ~/.local/bin/pip  1
# install vuejs
sudo npm install -g @vue/cli
###########
docker pull jenkins/jenkins:jdk11
docker-machine env jenkins
# paste to fill the blank
docker exec -it --user root <<container name>> /bin/bash
apt update
apt install build-essential
snap install ngrok
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-346.0.0-linux-x86_64.tar.gz
