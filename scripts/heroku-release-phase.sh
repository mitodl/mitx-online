#!/usr/bin/env bash
set -eo pipefail
indent() {
	RE="s/^/       /"
	[ "$(uname)" == "Darwin" ] && sed -l "$RE" || sed -u "$RE"
}

MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
MANAGE_FILE=${MANAGE_FILE:2}

# Run migrations

echo "-----> Running django migrations"
python $MANAGE_FILE showmigrations --list 2>&1 | indent
python $MANAGE_FILE migrate --noinput 2>&1 | indent

echo
