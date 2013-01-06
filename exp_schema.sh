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

    # output create table statement for each table
    for tab in ${tables[@]}; do
      echo -n "create '$tab',"
      echo "describe '$tab'" | hbase shell | \
        sed -n '/^DESC/,/row(s)/p' | grep -v -E '(^DESC|row\(s\))' | cut -b -107 | tr -d '\n ' | \
        sed 's/.*FAMILIES=>\[\(.*\)\]}$/\1/'
      echo
    done
fi
