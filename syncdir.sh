#!/usr/bin/env bash

syncdir() {
    dir=$1
    if [ -z "$dir" ]; then
        dir=$(pwd)
    fi
    # validate dir
    if [ ! -d "$dir" ]; then
        echo "error: no such directory: $dir" >&2
    fi
    # make it a absolute path
    dir=$(cd $dir; pwd)
    dir=$(readlink -f $dir)
    hostname=$(hostname)

    slaves.sh rsync -av --update --delete "$hostname":"$dir"/ "$dir"/
}

# main
if [ "$BASH_SOURCE" == "$0" ]; then
    if [ $# -eq 0 ]; then
        echo -n "Are you sure to sync [$(pwd)]? [N/y]"
        read -n 1 -s choice
        echo
        if [ "$choice" != "y" ]; then
            exit 0
        fi
        set $(pwd)
    fi

    for dir in $@; do
        syncdir $dir
    done
fi
