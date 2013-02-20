#!/usr/bin/env bash

usage() {
  if [ ! -z "$1" ]; then
    echo "error: "$1 > &2x
  fi
  echo "imp_data.sh [-l|--list <table list>] [-p|--parallel <num>] -i|--input <input dir>" >&2
  echo "  Note: <input dir> should always be the directory containing table sub-directries." >&2
}

get_tables() {
  local tablist=$1
  local indir=$2
  if [ -z "$tablist" ]; then
    local tab_dirs=( $(hadoop fs -ls $indir | grep -E '^d' | awk '{print $8}') )
    for dir in ${tab_dirs[@]}; do
      echo $(basename $dir)
    done
  else
    cat $1
  fi
}

import_tab() {
  local tab=$1
  local indir=$2
  echo "Start importing $tab at "$(date "+%Y-%m-%d %H:%M:%S")"..."
  hbase org.apache.hadoop.hbase.mapreduce.Import "$tab" "$indir"
  echo "End importing $tab at"$(date "+%Y-%m-%d %H:%M:%S")"."
}

# main
if [ "$BASH_SOURCE" == "$0" ]; then
  OPT_PARSE=$(getopt -o l:p:i:h -l list:,parallel:,input:,help \
    -n 'imp_data.sh' -- "$@")
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
      -i|--input)
        input_dir=$2; shift 2;;
      -h|--help)
        usage; exit 0;;
      --)
        shift; break;;
      *)
        usage "invalid option -- '"$1"'"; exit 1;;
    esac
  done

  # check required -i|--input
  if [ -z "$input_dir" ]; then
    usage "-i|--input is required"
    exit 1
  fi

  # default value for optional arguments
  table_list=${table_list:-""}
  parallel=${parallel:-"1"}

  # get list from table names
  tables=( $(get_tables "$table_list" "$input_dir") )

  for tab in ${tables[@]}; do
    import_tab "$tab" "$input_dir"/"$tab" &
    # wait if too many parallel importings
    jobnum=$(jobs -p | wc -l)
    while [ "$jobnum" -gt "$parallel" ]; do
      sleep 0.1s
      jobnum=$(jobs -p | wc -l)
    done
  done

  wait
  echo "Import ${#tables[@]} tables done."
fi
