#!/usr/bin/env bash

# get list from table names
tables=( $(echo 'list' | hbase shell | sed -n '/^TABLE/,/row(s)/p' | grep -v -E '(^TABLE|row\(s\))') )

# output create table statement for each table
for tab in ${tables[@]}; do
  echo -n "create '$tab',"
  echo "describe '$tab'" | hbase shell | \
    sed -n '/^DESC/,/row(s)/p' | grep -v -E '(^DESC|row\(s\))' | cut -b -107 | tr -d '\n ' | \
    sed 's/.*FAMILIES=>\[\(.*\)\]}$/\1/'
  echo
done
