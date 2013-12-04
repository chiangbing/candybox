#!/bin/env bash

# Simple utility to establish and monitor SSH reverse tunnels.
# See tunnels file to configure SSH reverse tunnels.

check_process() {
    local procnum=`ps -ef | grep "$*" | grep -v "grep" | wc -l`
    if [ $procnum -eq 1 ]; then
        echo "true"
    else 
        echo "false"
    fi
}

check_warnings() {
    local has_warnings=`grep -i warning sshtunnel_$1.log 2>&1`
    if [ "x$has_warnings" != "x" ]; then
        echo "true"
    else
        echo "false"
    fi
}

log_info() {
    echo "INFO ["`date`"] "$*
}

pid_of() {
    ps aux | grep "$*" | grep -v 'grep' | awk '{print $2}'
}


while [ 1 ] ; 
do
    while IFS='\n' read line; do
        params=( `echo $line | sed 's/\s/\n/g'` )
        tunnel_name=${params[0]}
        tunnel_opts=( ${params[@]:1:${#params[@]}} )
        if [ `check_warnings $tunnel_name` = "true" ]; then
            # kill the frozen ssh tunnel
            log_info "Warning detected for $tunnel_name, kill ssh tunnel $tunnel_name." 
            kill -9 `pid_of ${tunnel_opts}`
        fi

        if [ `check_process ${tunnel_opts[@]}` = "false" ]; then
            # restart the ssh tunnel if it does not exist
            log_info "ssh tunnel $tunnel_name not found, restarting..."
            log_info "$tunnel_name opts: $tunnel_opts[@]"
            ( /usr/bin/ssh -CNfg -R ${tunnel_opts[@]} ) > sshtunnel_"$tunnel_name".log 2>&1
        fi
    done < <(sed -e '/^\s*$/d' -e '/^#/d' tunnels)

    # check every 30 seconds
    sleep 30
done
