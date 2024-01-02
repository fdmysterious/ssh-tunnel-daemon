#!/bin/sh
# This script starts a given command, write the output stdout/stderr streams in /tmp/stdout,stderr.log files. It also
# writes the PID of the parent shell process in a temporary file.
# > This script is intended to be used with docker exec -d mode. Then, it can be stopped by calling docker exec with the correpsonding
# PID in stored file.

cmd="$1"
shift

echo $$ > /tmp/pidfile
exec ${cmd} $* > /tmp/stdout.log 2>/tmp/stderr.log
