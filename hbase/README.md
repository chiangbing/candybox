HBase Export/Import
-------------------

### exp_schema.sh
Export HBase table schemas (dump to stdout).
```bash
$ exp_schema.sh [-l|--list <table_list>]
```
The optional argument `table_list` should be a file containing a list of table name to be exported. If `table_list` is absent, then schema of all tables are dumped to stdout.
The dumped schema can be later executed in `hbase shell` to create tables.

### exp_data.sh
Export HBase table data to specified directory. (via [org.apache.hadoop.hbase.mapreduce.Export](http://hbase.apache.org/book/ops_mgt.html#export))
```bash
$ exp_data.sh [-l|--list <table_list>] [-p|--parallel <parallel_num>] -o|--output <output_dir>
```
If `table_list` is absent, all table data are exported to `output_dir`. If `table_list` is specified, only tables in `table_list` are exported. The exported data can be imported to current/another cluster later with `imp_data.sh`. Optional argument `parallel_num` indicates the maximum parallel running jobs.

### imp_data.sh
Import HBase table data from specified directory to tables. (via [org.apache.hadoop.hbase.mapreduce.Import](http://hbase.apache.org/book/ops_mgt.html#import) )
```bash
$ imp_data.sh [-l|--list <table_list>] [-p|--parallel <parallel_num>] -i|--input <input_dir>
```
If `table_list` is absent, all sub-directory names in `input_dir` is used as tables; or tables in `table_list` are to be imported. Optional argument `parallel_num` indicates the maximum parallel running jobs.
