#!/bin/bash

. REPLACELBPBINDIR/venv/bin/activate

ENVIRONMENT=$(cat /etc/environment)
export $ENVIRONMENT

REPLACELBPBINDIR/venv/bin/python3 REPLACELBPBINDIR/mqtt433.py --logfile=REPLACELBPLOGDIR/mqtt433.log --configfile=REPLACELBPCONFIGDIR/mqtt433.cfg

. REPLACELBPBINDIR/venv/bin/deactivate