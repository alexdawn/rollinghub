#!/usr/bin/env bash

set -e
set -u

 unset PGHOST
 unset PGPORT
 unset PGDATABASE
 export PGUSER=rollinghub

DATA_FILE=${1:-PGDATA}
DATABASE=${2:-rollinghub}
cd ~
set +e
initdb -D "$DATA_FILE" -E utf8 --no-locale -U "$PGUSER"
pg_ctl -D "$DATA_FILE" -l postgres.log start  # this needs to be done each reboot
set -e
createdb "$DATABASE"
