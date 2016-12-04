#!/usr/bin/env bash
set -e

BRANCH=raspilot-production

CURRENT_DIR=$(pwd)
echo "Loading new version"
cd ${RASPILOT_PATH}
git fetch --all > /dev/null
git checkout ${BRANCH} > /dev/null
git reset --hard origin/${BRANCH} > /dev/null
cd ${CURRENT_DIR}