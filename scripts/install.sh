#!/usr/bin/env bash

set -e

if grep -Fq "export RASPILOT_PATH=" ~/.bashrc; then
    echo "RASPILOT_PATH already SET"
else
    echo "export RASPILOT_PATH=$(pwd)" >> ~/.bashrc
    echo "RASPILOT_PATH is set to $(pwd)"
fi