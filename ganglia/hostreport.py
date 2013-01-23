#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# This script generate CPU/Memory/Disk/Network report by reading
# rrd files collecting by Ganglia. It generate similar graphs to
# which you can view in ganglia, but it provide a batch generating
# method.


import argparse
import rrdtool
import glob
import os
from os import path
from collections import deque
from datetime import datetime

import color


def plot_disk(start_time, end_time, host, rrd_dir, result_path):
    '''Plot a disk utilization for all disks'''
    colors = deque([color.CRIMSON, color.DODGERBLUE], maxlen=2)
    offset = color.Color(50, 50, 50)

    disk_rrds = glob.glob('%s/sd*.rrd' % rrd_dir)
    args = [
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time.strftime('%s'),
        '--end', end_time.strftime('%s'),
        '--vertical-label', 'Percent',
        '--title', 'Disk Utilization',
        '--upper-limit', '100']
    for d in disk_rrds:
        dname = path.splitext(path.basename(d))[0]
        rrd_path = path.join(rrd_dir, d)
        dcolor = colors.popleft()
        args.extend([
            'DEF:%s=%s:sum:AVERAGE' % (dname, rrd_path),
            'AREA:%s%s:%s:STACK' % (dname, dcolor, dname)])
        colors.append(dcolor + offset)
    args.extend(['-m', '2'])


def plot_mem(start_time, end_time, host, rrd_dir, result_path):
    '''Plot a mem report.'''
    color_used = color.DODGERBLUE
    color_cached = color.LIMEGREEN
    color_buffer = color.SPRINGGREEN
    color_free = color.ALICEBLUE
    path_total = path.join(rrd_dir, 'mem_total.rrd')
    path_free = path.join(rrd_dir, 'mem_free.rrd')
    path_cached = path.join(rrd_dir, 'mem_cached.rrd')
    path_buffer = path.join(rrd_dir, 'mem_buffers.rrd')

    rrdtool.graph(
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time.strftime('%s'),
        '--end', end_time.strftime('%s'),
        '--vertical-label', 'Bytes',
        '--title', '%s Memory Report' % host,
        'DEF:total=%s:sum:AVERAGE' % path_total,
        'DEF:free=%s:sum:AVERAGE' % path_free,
        'DEF:cached=%s:sum:AVERAGE' % path_cached,
        'DEF:buffer=%s:sum:AVERAGE' % path_buffer,
        'CDEF:used=total,free,-,cached,-,buffer,-',
        'AREA:used%s:used:STACK' % color_used,
        'AREA:cached%s:cached:STACK' % color_cached,
        'AREA:buffer%s:buffer:STACK' % color_buffer,
        'AREA:free%s:free:STACK' % color_free,
        '-m', '2',
        '--lower-limit', '0',
        '--rigid')


def plot_network(start_time, end_time, host, rrd_dir, result_path):
    '''Plot a network report.'''
    color_in = color.DODGERBLUE
    color_out = color.CRIMSON
    path_in = path.join(rrd_dir, 'bytes_in.rrd')
    path_out = path.join(rrd_dir, 'bytes_out.rrd')

    rrdtool.graph(
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time.strftime('%s'),
        '--end', end_time.strftime('%s'),
        '--vertical-label', 'Bytes',
        '--title', '%s Network Report' % host,
        'DEF:in=%s:sum:AVERAGE' % path_in,
        'DEF:out=%s:sum:AVERAGE' % path_out,
        'LINE1:in%sBB:in' % color_in,
        'LINE1:out%sBB:out' % color_out,
        '-m', '2')


def plot_cpu(start_time, end_time, host, rrd_dir, result_path):
    '''Plot a CPU report.'''
    color_user = color.DODGERBLUE
    color_system = color.CRIMSON
    color_waitio = color.MAGENTA
    color_nice = color.YELLOW
    path_user = path.join(rrd_dir, 'cpu_user.rrd')
    path_system = path.join(rrd_dir, 'cpu_system.rrd')
    path_waitio = path.join(rrd_dir, 'cpu_wio.rrd')
    path_nice = path.join(rrd_dir, 'cpu_nice.rrd')

    rrdtool.graph(
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time.strftime('%s'),
        '--end', end_time.strftime('%s'),
        '--vertical-label', 'Percent',
        '--title', '%s CPU Report' % host,
        '--upper-limit', '100',
        'DEF:user=%s:sum:AVERAGE' % path_user,
        'DEF:system=%s:sum:AVERAGE' % path_system,
        'DEF:waitio=%s:sum:AVERAGE' % path_waitio,
        'DEF:nice=%s:sum:AVERAGE' % path_nice,
        'AREA:user%s:user:STACK' % color_user,
        'AREA:system%s:system:STACK' % color_system,
        'AREA:waitio%s:waitio:STACK' % color_waitio,
        'AREA:nice%s:nice:STACK' % color_nice,
        '-m', '2')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Host report plotter.')
    parser.add_argument('--result', metavar='RESULT_DIR', help='result directory to put report files.')
    parser.add_argument('--start', metavar='START_TIME', help='start time of report')
    parser.add_argument('--end', metavar='END_TIME', help='end_time of report')
    parser.add_argument(
        'rrds',
        help='one or many directories each containing rrds for one host.',
        nargs='+')
    args = parser.parse_args()
    start_time = datetime.strptime(args.start, '%Y%m%d%H%M%S')
    end_time = datetime.strptime(args.end, '%Y%m%d%H%M%S')
    result_dir = args.result

    if not path.exists(result_dir):
        os.mkdir(result_dir)

    for rrd in args.rrds:
        host = path.splitext(path.basename(rrd))[0]
        plot_cpu(start_time, end_time, host, rrd, path.join(result_dir, '%s_cpu.png' % host))
        plot_mem(start_time, end_time, host, rrd, path.join(result_dir, '%s_mem.png' % host))
        plot_disk(start_time, end_time, host, rrd, path.join(result_dir, '%s_disk.png' % host))
        plot_network(start_time, end_time, host, rrd, path.join(result_dir, '%s_network.png' % host))
