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
    table_list=$1

    # get list from table names
    tables=( $(get_tables $table_list) )

    # output create table statement for each table
    for tab in ${tables[@]}; do
      echo -n "create '$tab', "
      echo "describe '$tab'" | hbase shell | \
        awk 'BEGIN { x = 0 } 
            { if ($0 ~ /^DESC/) { 
                x=1; next; 
              } 
              if ($0 ~ /row\(s\)/) x=0; 
              if (x == 1) { 
                match($0, /FAMILIES => \[(.*)\]/, arr); 
                print arr[1]
              }
            }'
    done
fi
