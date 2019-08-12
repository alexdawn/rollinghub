 unset PGHOST
 unset PGPORT
 unset PGDATABASE
 export PGUSER=rollinghub

cd
initdb -D PGDATA -E utf8 --no-locale -U $PGUSER
pg_ctl -D "PGDATA" -l postgres.log start
createdb

#this needs to be done each reboot
pg_ctl -D "PGDATA" -l postgres.log start