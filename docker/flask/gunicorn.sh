#!/bin/sh
/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 --chdir=/app/src agentless.app:app
