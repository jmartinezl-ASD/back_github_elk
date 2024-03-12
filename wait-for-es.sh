#!/bin/sh

set -e

host="$1"
shift
cmd="$@"

until curl -s http://"$host":9200/; do
  >&2 echo "Elasticsearch is unavailable - sleeping"
  sleep 1
done

>&2 echo "Elasticsearch is up - executing command"
exec $cmd
