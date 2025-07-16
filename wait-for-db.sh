#!/usr/bin/env bash
# wait-for-it.sh: wait until a host:port is available

hostport="$1"
shift
cmd="$@"

host="${hostport%:*}"
port="${hostport#*:}"

echo "Waiting for $host:$port to be ready..."
while ! nc -z "$host" "$port"; do
  sleep 1
done

echo "$host:$port is up - executing command"
exec $cmd
