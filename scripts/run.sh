#!/usr/bin/env bash

set -e

RASPILOT_ROOT=/home/raspilot/raspilot-app

PYTHONPATH=${RASPILOT_ROOT} python3.5 ${RASPILOT_ROOT}/new_raspilot/raspilot_implementation/main.py
