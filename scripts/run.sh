#!/usr/bin/env bash

source ~/.bashrc
source ~/.bash_profile

set -e

BRANCH=raspilot-production
CONFIG_PATH=new_raspilot/config/config.cfg

if grep -iq "autoupdate\s*=\s*enabled" ${RASPILOT_PATH}/${CONFIG_PATH}; then
echo "Loading new version"
    git fetch --all > /dev/null
    git checkout ${BRANCH} > /dev/null
    git reset --hard origin/${BRANCH} > /dev/null
else
    echo "Autoupdate Disabled"
fi

echo "Starting Raspilot"
PYTHONPATH=${RASPILOT_PATH} python3.5 ${RASPILOT_PATH}/new_raspilot/raspilot_implementation/main.py
