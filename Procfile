web: bin/start-nginx bin/start-pgbouncer newrelic-admin run-program uwsgi uwsgi.ini
worker: bin/start-pgbouncer newrelic-admin run-program celery -A main.celery:app worker -E -Q hubspot_sync,celery -B -l $MITX_ONLINE_LOG_LEVEL
extra_worker: bin/start-pgbouncer newrelic-admin run-program celery -A main.celery:app worker -E -Q hubspot_sync,celery -l $MITX_ONLINE_LOG_LEVEL
