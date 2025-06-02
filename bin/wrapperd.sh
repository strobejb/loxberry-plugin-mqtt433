#!/bin/bash

PLUGINNAME=REPLACELBPPLUGINDIR
PATH="/sbin:/bin:/usr/sbin:/usr/bin:$LBHOMEDIR/bin:$LBHOMEDIR/sbin"

ENVIRONMENT=$(cat /etc/environment)
export $ENVIRONMENT

# Logfile
. $LBHOMEDIR/libs/bashlib/loxberry_log.sh
PACKAGE=${PLUGINNAME}
NAME=${PLUGINNAME}
LOGDIR=$LBPLOG/${PLUGINNAME}

# 
LOGPATH=REPLACELBPLOGDIR/${PLUGINNAME}.log
CONFIGPATH=REPLACELBPCONFIGDIR/${PLUGINNAME}.cfg

# Debug output
#STDERR=0
#DEBUG=0

if [[ ${LOGLEVEL} -eq 7 ]]; then
	LOGINF "Debugging is enabled! This will produce A LOT messages in your logfile!"
	STDERR=1
	DEBUG=1
fi

LOGSTART "$PLUGINNAME"
LOGINF "Starting ${PLUGINNAME} ($1) wrapper script."
echo "Running with LOGLEVEL ${LOGLEVEL}: ${LOGPATH}"

case "$1" in
  start|restart)

	#echo $HOSTNAME"/gpio/#" > $LBHOMEDIR/config/plugins/${PLUGINNAME}/mqtt_subscriptions.cfg
	
	if [ "$1" = "restart" ]; then
		LOGINF "Stopping ${PLUGINNAME}..."
		pkill -f "REPLACELBPBINDIR/${PLUGINNAME}.py" >> ${LOGPATH} 2>&1
	fi

	if [ "$(pgrep -f "REPLACELBPBINDIR/${PLUGINNAME}.py")" ]; then
		LOGINF "${PLUGINNAME}.py already running."
		LOGEND "${PLUGINNAME}"
		exit 0
	fi

    # activate python virtual environment
    echo "Starting ${PLUGINNAME}..."
    LOGINF "Starting ${PLUGINNAME}..."
    . REPLACELBPBINDIR/venv/bin/activate

    # execute and detach
    REPLACELBPBINDIR/venv/bin/python3 "REPLACELBPBINDIR/${PLUGINNAME}.py" --logfile ${LOGPATH} --loglevel ${LOGLEVEL} --configfile "${CONFIGPATH}" &
    # > /dev/null 2>&1
    
    # done!
    deactivate
    LOGEND "${PLUGINNAME}"
    exit 0
    ;;

  stop)

	LOGINF "Stopping ${PLUGINNAME}..."
	pkill -f "REPLACELBPBINDIR/${PLUGINNAME}.py" >> ${LOGPATH} 2>&1

	if [ "$(pgrep -f "REPLACELBPBINDIR/${PLUGINNAME}.py")" ]; then
		LOGERR "${PLUGINNAME}.py could not be stopped."
	else
		LOGOK "${PLUGINNAME}.py stopped successfully."
	fi

	LOGEND "${PLUGINNAME}"
        exit 0
        ;;

  *)
    echo "Usage: $0 [start|stop|restart]" >&2
	LOGINF "No command given. Exiting."
	LOGEND "${PLUGINNAME}"
        exit 0
  ;;

esac

LOGEND "${PLUGINNAME}"
