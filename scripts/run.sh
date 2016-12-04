#!/usr/bin/env bash

set -e

UPDATE_SCRIPT_PATH=scripts/update.sh
CONFIG_PATH=new_raspilot/config/config.cfg

if grep -iq "autoupdate\s*=\s*enabled" ${RASPILOT_PATH}/${CONFIG_PATH}; then
    ${RASPILOT_PATH}/${UPDATE_SCRIPT_PATH}
else
    echo "Autoupdate Disabled"
fi

echo "Starting Raspilot"
PYTHONPATH=${RASPILOT_PATH} python3.5 ${RASPILOT_PATH}/new_raspilot/raspilot_implementation/main.py
