#!/bin/bash
set -e

# Runs python script within virtualenv
DIRECTORY=$(dirname $0)
source "${DIRECTORY}/venv/bin/activate"
python "${@:1}"
