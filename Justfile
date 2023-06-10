start:
	#!/usr/bin/env bash
	if [ ! -d '.pids' ]; then
		mkdir '.pids'
	fi
	litestream replicate -config litestream.dev.yml &
	echo $! > .pids/litestream
	caddy run --config $CADDYFILE &
	echo $! > .pids/caddy

stop:
	#!/usr/bin/env bash
	if [ -d '.pids' ]; then
		for f in `ls .pids`; do
			kill $(cat .pids/$f)
			rm .pids/$f
		done
	fi

pulldb:
	#!/usr/bin/env bash
	rm ididitfor.db
	rm ididitfor.db-wal
	rm ididitfor.db-shm
	litestream restore -config litestream.dev.yml ./ididitfor.db
