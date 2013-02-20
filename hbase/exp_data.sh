#!/usr/bin/env bash

usage() {
  if [ ! -z "$1" ]; then
    echo "error: "$1 >&2
  fi
  echo "exp_data.sh [-l|--list <table list>] [-p|--parallel <num>] -o|--output <output dir>" >&2
}

get_tables() {
  if [ -z "$1" ]; then
    # -l/--list is not specified, get table list from hbase
    echo 'list' | hbase shell | sed -n '/^TABLE/,/row(s)/p' | grep -v -E '(^TABLE|row\(s\))'
  else
    cat $1
  fi
}

export_tab() {
  local tab=$1
  local outdir=$2
  echo "Start exporting $tab at "$(date +"%Y-%m-%d %H:%M:%S")"..."
  hbase org.apache.hadoop.hbase.mapreduce.Export "$tab" "$outdir"
  echo "End exporting $tab at "$(date +"%Y-%m-%d %H:%M:%S")"."
}

# main
if [ "$BASH_SOURCE" == "$0" ]; then
  OPT_PARSE=$(getopt -o l:p:o:h -l list:,parallel:,output:,help \
    -n 'exp_data.sh' -- "$@")
  if [ "$?" -ne "0" ]; then
    usage
    exit 1
  fi
  eval set -- "$OPT_PARSE"
  
  while true; do
    case $1 in
      -l|--list)
        table_list=$2; shift 2;;
      -p|--parallel)
        parallel=$2; shift 2;;
      -o|--output)
        output_dir=$2; shift 2;;
      -h|--help)
        usage; exit 0;;
      --)
        shift; break;;
      *)
        usage "invalid option -- '"$1"'"; exit 1;;
    esac
  done

  # check required -o|--output
  if [ -z "$output_dir" ]; then
    usage "-o|--output is required"
    exit 1
  fi

  # default value for optional arguments
  table_list=${table_list:-""}
  parallel=${parallel:-"1"}

  # get list from table names
  tables=( $(get_tables $table_list) )

  for tab in ${tables[@]}; do
    export_tab "$tab" "$output_dir"/"$tab" &
    # wait if too many parallel exportings
    jobnum=$(jobs -p | wc -l)
    while [ "$jobnum" -gt "$parallel" ]; do
      sleep 0.1s
      jobnum=$(jobs -p | wc -l)
    done
  done

  wait
  echo "Export ${#tables[@]} tables done."
fi
