#!/usr/bin/env bash

get_tables() {
    if [ -z "$1" ]; then
        tab_dirs=( $(hadoop fs -ls /import | grep -E '^d' | awk '{print $8}') )
        for dir in ${tab_dirs}; do
            echo $(basename $dir)
        done
    else
        cat $1
    fi
}


# main
if [ "$BASH_SOURCE" == "$0" ]; then
    if [ -z "$1" ]; then
        echo "$0 <inputdir> [tablelist]" >&2
        exit 1
    fi

    input_dir=$1
    shift 1
    table_list=$1

    # get list from table names
    tables=( $(get_tables $table_list) )

    for tab in ${tables[@]}; do
        echo "Start importing $tab at "$(date "+%Y-%m-%d %H:%M:%S")"..."
        hbase org.apache.hadoop.hbase.mapreduce.Import "$tab" "$input_dir"/"$tab"
        echo "End importing $tab at"$(date "+%Y-%m-%d %H:%M:%S")"."
    done
fi
