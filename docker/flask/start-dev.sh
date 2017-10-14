#!/bin/sh
python -m agentless db upgrade
python -m agentless runserver -h 0.0.0.0 -p 8000
