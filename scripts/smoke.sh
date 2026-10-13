#!/usr/bin/env sh
set -eu

curl --fail --silent --show-error http://localhost:8000/health/live
printf '\n'
curl --fail --silent --show-error http://localhost:8000/health/ready
printf '\n'
