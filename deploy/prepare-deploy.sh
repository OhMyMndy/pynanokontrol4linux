#!/usr/bin/env bash



sudo apt-get install libasound2-dev build-essential libasound2-dev libjack-jackd2-dev -y

python3 -m venv ./venv

source ./venv/bin/activate


pip3 install -r requirements.txt
