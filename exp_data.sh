#!/usr/bin/env bash

get_tables() {
    if [ -z "$1" ]; then
        echo 'list' | hbase shell | sed -n '/^TABLE/,/row(s)/p' | grep -v -E '(^TABLE|row\(s\))'
    else
        cat $1
    fi
}


# main
if [ "$BASH_SOURCE" == "$0" ]; then
    if [ -z "$1" ]; then
        echo "$0 <outputdir> [tablelist]" >&2
        exit 1
    fi

    output_dir=$1
    shift 1
    table_list=$1

    # get list from table names
    tables=( $(get_tables $table_list) )

    for tab in ${tables[@]}; do
        echo "Start exporting $tab at "$(date "+%Y-%m-%d %H:%M:%S")"..."
        hbase org.apache.hadoop.hbase.mapreduce.Export "$tab" "$output_dir"/"$tab"
        echo "End exporting $tab at"$(date "+%Y-%m-%d %H:%M:%S")"."
    done
fi
