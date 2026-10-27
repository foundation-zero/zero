#!/bin/sh
/usr/local/bin/create-local-users.sh &
exec /run.sh "$@"
