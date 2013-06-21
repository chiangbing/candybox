#!/usr/bin/env bash


if [ ! -z "$HADOOP_HOME" ]; then
    HADOOP=$HADOOP_HOME/bin/hadoop
else
    HADOOP=$(which hadoop 2>/dev/null)
fi

if [ ! -x "$HADOOP" ]; then
    echo "ERROR: bin/hadoop not found." >&2
    exit 1
fi


usage() {
    echo "./dfs_pput.sh -p <processes> -s <slaves file> [--snappy] [-r <replications>] <source> [<source> ...] <dest>" >&2
    exit 1
}

make_localput() {
    cat > $1 <<'EOF'
HADOOP=$1
shift
parallel=$1
shift
use_snappy=$1
shift
snappyzip_jar=$1
shift
replicas=$1
shift
dest=${@: -1}
srcs=${@:1:$#-1}

put_file() {
    local src_file=$1
    local dest_dir=$2

    hadoop_opts=""
    if [ "$replicas" -gt "0" ]; then
        hadoop_opts="-Ddfs.replication=$replicas"
    fi

    echo "Start to put $src_file to $dest_dir."
    if [ "$use_snappy" == "true" ]; then
        zip_name=$(basename $src_file)".snappy"
        $HADOOP jar $snappyzip_jar com.hanborq.SnappyZip $src_file - | \
            $HADOOP fs $hadoop_opts -put - $dest_dir/$zip_name
    else
        $HADOOP fs $hadoop_opts -put $src_file $dest_dir/
    fi
    echo "Put $src_file to $dest_dir done."
}

for s in ${srcs[@]}; do
    if [ -f $s ]; then
        put_file $s $dest &
    else
        for f in $(find $s -maxdepth 1 -mindepth 1 2>/dev/null); do
            put_file $f $dest &

            # block until one or more put_file done
            jobs_num=$(jobs -rp | wc -l)
            while [ "$jobs_num" -ge "$parallel" ]; do
                sleep 0.1s
                jobs_num=$(jobs -rp | wc -l)
            done
        done
    fi

    # block until one or more put_file done
    jobs_num=$(jobs -rp | wc -l)
    while [ "$jobs_num" -ge "$parallel" ]; do
        sleep 0.1s
        jobs_num=$(jobs -rp | wc -l)
    done
done

# wait background jobs to complete
wait
EOF
    chmod +x $1
}

abs_paths() {
    for p in $@; do
        if [ -f $p ]; then
            pdir=$(dirname $p)
            echo $(cd $pdir 2>/dev/null && pwd)"/"$(basename $p)
        else
            echo $(cd $p 2>/dev/null && pwd)
        fi
    done
}


# main
if [ "$BASH_SOURCE" == "$0" ]; then
    OPT_PARSE=$(getopt -o p:s:r:h -l parallel:,slaves:,replication:,snappy,help \
        -n 'dfs_pput.sh' -- "$@")
    if [ "$?" -ne "0" ]; then
        usage
        exit 1
    fi
    eval set -- "$OPT_PARSE"

    while true; do
        case $1 in
            -p|--parallel)
                parallel=$2; shift 2;;
            -s|--slaves)
                slaves_file=$2; shift 2;;
            -r|--replication)
                replicas=$2; shift 2;;
            --snappy)
                use_snappy=true; shift;;
            -h|--help)
                usage; exit 0;;
            --)
                shift; break;;
            *)
                usage "invalid option -- '"$1"'"; exit 1;;
        esac
    done

    # at least two parameters remaining to use as source and dest
    if [ $# -lt 2 ]; then
        echo "ERROR: missing sources or destination." >&2
        usage
        exit 1
    fi

    use_snappy=${use_snappy:-false}
    replicas=${replicas:-0}

    if [ "$use_snappy" == "true" ]; then
        # check snappyzip tool
        # if multiple version is found, use the max version one
        snappyzip_jar=$(ls snappyzip-*.jar | tail -1)
        if [ -z "$snappyzip_jar" -o ! -e "$snappyzip_jar" ]; then
            echo "ERROR: cannot find snappyzip jar in current directory." >&2
            exit 1
        fi
    fi

    if [ -z "$parallel" ]; then
        echo "INFO: use default parallel: 20."
        parallel=20
    fi

    if [ -z "$slaves_file" ]; then
        echo "INFO: use local mode."
        local_mode=true
    else
        local_mode=false
        slaves=( $(grep -E -v '^#' $slaves_file) )
    fi

    dest=${@: -1}
    # check dest directory(on HDFS)
    $HADOOP fs -test -d "$dest" 2> /dev/null
    if [ ! $? -eq 0 ]; then
        echo "INFO: $dest not exists, create it at HDFS."
        $HADOOP fs -mkdir $dest
    fi

    srcs=${@:1:$#-1}
    # make srcs absolute path
    srcs=( $(abs_paths ${srcs[@]}) )

    # create local put script at tmp
    mytmp=/tmp/$USER/distput
    mkdir -p $mytmp
    make_localput $mytmp/localput.sh
    if [ "$use_snappy" == "true" ]; then
        cp $snappyzip_jar $mytmp/$snappyzip_jar
    fi


    if [ "$local_mode" == "true" ]; then
        echo "INFO: run put locally ..."
        $mytmp/localput.sh $HADOOP \
            $parallel \
            $use_snappy $mytmp/$snappyzip_jar \
            $replicas \
            ${srcs[@]} $dest
    else
        # dist mode:
        # distribute localput.sh to slaves and execute it at remote end
        for slave in ${slaves[@]}; do
            ssh $slave mkdir -p $mytmp
            if [ "$use_snappy" == "true" ]; then
                scp $mytmp/localput.sh $mytmp/$snappyzip_jar $slave:$mytmp
            else
                scp $mytmp/localput.sh $slave:$mytmp
            fi
            echo "INFO: start localput.sh at $slave"
            ssh $slave $mytmp/localput.sh $HADOOP \
                $parallel \
                $use_snappy $mytmp/$snappyzip_jar \
                $replicas \
                ${srcs[@]} $dest \
                2\>\&1 \| tee $mytmp/localput.log | sed "s/^/$slave: /" &
        done

        wait
    fi

    echo "All done."
fi # end of main
