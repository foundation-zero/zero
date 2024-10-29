#!/bin/sh
pip3 install -r .devcontainer/requirements.txt

sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo curl -fsSL http://build.openmodelica.org/apt/openmodelica.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/openmodelica-keyring.gpg

echo "deb [arch=arm64 signed-by=/usr/share/keyrings/openmodelica-keyring.gpg] \
  https://build.openmodelica.org/apt \
  bookworm \
  stable" | sudo tee /etc/apt/sources.list.d/openmodelica.list

sudo apt update
sudo apt install openmodelica