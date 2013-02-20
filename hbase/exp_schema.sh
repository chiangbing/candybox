#!/usr/bin/env bash

usage() {
  if [ ! -z "$1" ]; then
    echo "error: "$1 >&2
  fi
  echo "usage: exp_schema.sh [-l|--list <table list>]" >&2
}

get_tables() {
  if [ -z "$1" ]; then
    # -l/--list is not specified, get table list from hbase
    echo 'list' | hbase shell | sed -n '/^TABLE/,/row(s)/p' | grep -v -E '(^TABLE|row\(s\))'
  else
    cat $1
  fi
}


# main

if [ "$BASH_SOURCE" == "$0" ]; then
  OPT_PARSE=$(getopt -o l:h -l list:,help -n 'exp_schema.sh' -- "$@")
  if [ "$?" -ne "0" ]; then
    usage
    exit 1
  fi
  eval set -- "$OPT_PARSE"

  while true; do
    case "$1" in
      -l|--list) table_list=$2; shift 2;;
      -h|--help) usage; exit 0;;
      --) shift; break;;
      *) usage "invalid option -- '"$1"'"; exit 1;;
    esac
  done

  # default value for optional arguments
  table_list=${table_list:-""}

  # get list from table names
  tables=( $(get_tables $table_list) )

  # output create table statement for each table
  for tab in ${tables[@]}; do
    echo -n "create '$tab',"
    echo "describe '$tab'" | hbase shell | \
    awk 'BEGIN { x = 0; schema = ""; }
      { if ($0 ~ /^DESC/) { x=1; next; }
        if ($0 ~ /row\(s\)/) { x=0; }
        if (x == 0) { next; }
        gsub(/[ \t\v\n\r\f]/, "");
        if (x == 1) {
        gsub(/(true|false)$/, "");
        x += 1;
        }
        schema = (schema $0);
      }
      END { match(schema, /FAMILIES=>\[(.*)\]\}$/, arr); print arr[1]; }'
  done
fi
