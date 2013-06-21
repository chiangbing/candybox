#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script generate CPU/Memory/Disk/Network report by reading
# rrd files collecting by Ganglia. It generate similar graphs to
# which you can view in ganglia, but it provide a batch generating
# method.


import optparse
import rrdtool
import re
import os
from os import path
from collections import deque
from datetime import datetime


###### Colors ######

_COLORS = ['#E00000',
           '#E06000',
           '#E0C000',
           '#A0E000',
           '#40E000',
           '#00E020',
           '#00E080',
           '#00E0E0',
           '#0080E0',
           '#0020E0',
           '#4000E0',
           '#A000E0',
           '#E000C0',
           '#E00060']
_STACK_COLORS = deque(_COLORS)


def _next_stack_color():
    color = _STACK_COLORS.popleft()
    _STACK_COLORS.append(color)
    return color


def _reset_stack_color():
    global _STACK_COLORS
    _STACK_COLORS = deque(_COLORS)


####### Helper Functions ######

def _extract_hostname(host_rrd):
    """Extract hostname from directory name."""
    return path.splitext(path.basename(host_rrd))[0]


def _grep_rrds(rrd_dir, pattern, result_key=None):
    """Find out rrd that match the specified pattern."""
    if result_key is None:
        rrds = []
    else:
        rrds = {}
    for f in os.listdir(rrd_dir):
        p = os.path.join(rrd_dir, f)
        if not os.path.isfile(p):
            continue
        m = re.search(pattern, f)
        if m is not None:
            # match!
            if result_key is None:
                rrds.append(p)
            else:
                rrds[m.group(result_key)] = p
    return rrds


ONE_DAY_SECS = 86400
ONE_HOUR_SECS = 3600


def _get_time_range(rrd, opts):
    """Get a time range for generate report from rrd."""
    start_time = None
    end_time = None
    if opts.start_time is not None and opts.end_time is not None:
        start_time = opts.start_time.strftime('%s')
        end_time = opts.end_time.strftime('%s')
    if opts.last_day:
        end_time = rrdtool.last(rrd)
        start_time = end_time - ONE_DAY_SECS
    if opts.last_hour:
        end_time = rrdtool.last(rrd)
        start_time = end_time - ONE_HOUR_SECS
    return str(start_time), str(end_time)


def _gen_title(host, type_, opts):
    title = '%s %s' % (host, type_)
    if opts.last_day:
        title += ' last day'
    elif opts.last_hour:
        title += ' last hour'
    return title


###### Plot Functions #######

def plot_disk_util(host_rrd, opts):
    """Plot a disk utilization for all disks."""
    _reset_stack_color()
    hostname = _extract_hostname(host_rrd)
    result_path = os.path.join(opts.result_dir, '%s_disk_util.png' % hostname)
    # find out rrds for disk util
    disk_rrds = _grep_rrds(host_rrd, opts.disk_util_pattern, 'disk')
    start_time, end_time = _get_time_range(disk_rrds.itervalues().next(), opts)
    args = [result_path,
            '--imgformat', 'PNG',
            '--start', start_time,
            '--end', end_time,
            '--vertical-label', 'Percent',
            '--title', _gen_title(hostname, 'Disk Util', opts),
            '--slope-mode']
    for disk in sorted(disk_rrds):
        rrd = disk_rrds[disk]
        color = _next_stack_color()
        args.extend([
            'DEF:%s=%s:sum:AVERAGE' % (disk, rrd),
            'AREA:%s%s:%s:STACK' % (disk, color, disk)])
    args.extend(['-m', '2'])
    rrdtool.graph(*args)


def plot_disk_read_rate(host_rrd, opts):
    """Plot a disk read rate for all disks."""
    _reset_stack_color()
    hostname = _extract_hostname(host_rrd)
    result_path = os.path.join(opts.result_dir,
                               '%s_disk_read_rate.png' % hostname)
    # find out rrds for disk util
    disk_rrds = _grep_rrds(host_rrd, opts.disk_read_rate_pattern, 'disk')
    start_time, end_time = _get_time_range(disk_rrds.itervalues().next(), opts)
    args = [result_path,
            '--imgformat', 'PNG',
            '--start', start_time,
            '--end', end_time,
            '--vertical-label', 'Bytes/Sec',
            '--title', _gen_title(hostname, 'Disk Read', opts),
            '--slope-mode']
    for disk in sorted(disk_rrds):
        rrd = disk_rrds[disk]
        color = _next_stack_color()
        args.extend([
            'DEF:%s=%s:sum:AVERAGE' % (disk, rrd),
            'AREA:%s%s:%s:STACK' % (disk, color, disk)])
    args.extend(['-m', '2'])
    rrdtool.graph(*args)


def plot_disk_write_rate(host_rrd, opts):
    """Plot a disk write rate for all disks."""
    _reset_stack_color()
    hostname = _extract_hostname(host_rrd)
    result_path = os.path.join(opts.result_dir,
                               '%s_disk_write_rate.png' % hostname)
    # find out rrds for disk util
    disk_rrds = _grep_rrds(host_rrd, opts.disk_write_rate_pattern, 'disk')
    start_time, end_time = _get_time_range(disk_rrds.itervalues().next(), opts)
    args = [result_path,
            '--imgformat', 'PNG',
            '--start', start_time,
            '--end', end_time,
            '--vertical-label', 'Bytes/Sec',
            '--title', _gen_title(hostname, 'Disk Write', opts),
            '--slope-mode']
    for disk in sorted(disk_rrds):
        rrd = disk_rrds[disk]
        color = _next_stack_color()
        args.extend([
            'DEF:%s=%s:sum:AVERAGE' % (disk, rrd),
            'AREA:%s%s:%s:STACK' % (disk, color, disk)])
    args.extend(['-m', '2'])
    rrdtool.graph(*args)


def plot_mem(host_rrd, opts):
    """Plot a mem report."""
    mem_used_color = '#5555CC'
    mem_cached_color = '#33CC33'
    mem_buffered_color = '#99FF33'
    mem_shared_color = '#0000AA'
    mem_swapped_color = '#9900CC'
    mem_total_color = '#FF0000'
    mem_total_rrd = path.join(host_rrd, 'mem_total.rrd')
    mem_free_rrd = path.join(host_rrd, 'mem_free.rrd')
    mem_cache_rrd = path.join(host_rrd, 'mem_cached.rrd')
    mem_buffer_rrd = path.join(host_rrd, 'mem_buffers.rrd')
    mem_shared_rrd = path.join(host_rrd, 'mem_shared.rrd')
    swap_total_rrd = path.join(host_rrd, 'swap_total.rrd')
    swap_free_rrd = path.join(host_rrd, 'swap_free.rrd')
    hostname = _extract_hostname(host_rrd)
    start_time, end_time = _get_time_range(mem_total_rrd, opts)
    result_path = os.path.join(opts.result_dir, '%s_mem.png' % hostname)
    args = [
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time,
        '--end', end_time,
        '--vertical-label', 'Bytes',
        '--title', _gen_title(hostname, 'Memory', opts),
        '--lower-limit', '0',
        '--rigid',
        'DEF:_total=%s:sum:AVERAGE' % mem_total_rrd,
        'DEF:_free=%s:sum:AVERAGE' % mem_free_rrd,
        'DEF:_cached=%s:sum:AVERAGE' % mem_cache_rrd,
        'DEF:_buffer=%s:sum:AVERAGE' % mem_buffer_rrd,
        'DEF:_shared=%s:sum:AVERAGE' % mem_shared_rrd,
        'DEF:_swap_total=%s:sum:AVERAGE' % swap_total_rrd,
        'DEF:_swap_free=%s:sum:AVERAGE' % swap_free_rrd,
        'CDEF:total=_total,1024,*',
        'CDEF:free=_free,1024,*',
        'CDEF:cached=_cached,1024,*',
        'CDEF:buffer=_buffer,1024,*',
        'CDEF:used=total,free,-,cached,-,buffer,-',
        'CDEF:shared=_shared,1024,*',
        'CDEF:swap_total=_swap_total,1024,*',
        'CDEF:swap_free=_swap_free,1024,*',
        'CDEF:swap_used=swap_total,swap_free,-',
        'AREA:used%s:Memory Used:STACK' % mem_used_color,
        'AREA:shared%s:Memory Shared:STACK' % mem_shared_color,
        'AREA:cached%s:Memory Cached:STACK' % mem_cached_color,
        'AREA:buffer%s:Memory Buffered:STACK' % mem_buffered_color,
        'AREA:swap_used%s:Memory Swapped:STACK' % mem_swapped_color,
        'LINE1:total%s:Total In-Core Memory' % mem_total_color,
        '-m', '2',
        '--slope-mode']
    rrdtool.graph(*args)


def plot_network(host_rrd, opts):
    """Plot a network report."""
    color_in = '#33CC33'
    color_out = '#5555CC'
    net_in_rrd = path.join(host_rrd, 'bytes_in.rrd')
    net_out_rrd = path.join(host_rrd, 'bytes_out.rrd')
    hostname = _extract_hostname(host_rrd)
    start_time, end_time = _get_time_range(net_in_rrd, opts)
    result_path = os.path.join(opts.result_dir, '%s_net.png' % hostname)
    args = [
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time,
        '--end', end_time,
        '--vertical-label', 'Bytes',
        '--title', _gen_title(hostname, 'Network', opts),
        'DEF:in=%s:sum:AVERAGE' % net_in_rrd,
        'DEF:out=%s:sum:AVERAGE' % net_out_rrd,
        'LINE1:in%s:In' % color_in,
        'LINE1:out%s:Out' % color_out,
        '-m', '2',
        '--slope-mode']
    rrdtool.graph(*args)


def plot_cpu(host_rrd, opts):
    """Plot a CPU report."""
    cpu_user_color = '#3333BB'
    color_nice_colr = '#FFEA00'
    cpu_sys_color = '#DD0000'
    cpu_wait_color = '#FF8A60'
    cpu_idle_color = '#E2E2F2'
    cpu_user_rrd = path.join(host_rrd, 'cpu_user.rrd')
    cpu_sys_rrd = path.join(host_rrd, 'cpu_system.rrd')
    cpu_wait_rrd = path.join(host_rrd, 'cpu_wio.rrd')
    cpu_nice_rrd = path.join(host_rrd, 'cpu_nice.rrd')
    cpu_idle_rrd = path.join(host_rrd, 'cpu_idle.rrd')
    hostname = _extract_hostname(host_rrd)
    start_time, end_time = _get_time_range(cpu_user_rrd, opts)
    result_path = os.path.join(opts.result_dir, '%s_cpu.png' % hostname)
    args = [
        result_path,
        '--imgformat', 'PNG',
        '--start', start_time,
        '--end', end_time,
        '--vertical-label', 'Percent',
        '--title', '%s CPU Report' % hostname,
        'DEF:user=%s:sum:AVERAGE' % cpu_user_rrd,
        'DEF:system=%s:sum:AVERAGE' % cpu_sys_rrd,
        'DEF:wait=%s:sum:AVERAGE' % cpu_wait_rrd,
        'DEF:nice=%s:sum:AVERAGE' % cpu_nice_rrd,
        'DEF:idle=%s:sum:AVERAGE' % cpu_idle_rrd,
        'AREA:user%s:User CPU:STACK' % cpu_user_color,
        'AREA:nice%s:Nice CPU:STACK' % color_nice_colr,
        'AREA:system%s:System CPU:STACK' % cpu_sys_color,
        'AREA:wait%s:WAIT CPU:STACK' % cpu_wait_color,
        'AREA:idle%s:Idle CPU:STACK' % cpu_idle_color,
        '-m', '2',
        '--slope-mode']
    if hostname != '__SummaryInfo__':
        args.extend(['--upper-limit', '100', '--rigid'])
    rrdtool.graph(*args)


def _parse_args():
    """Parse command line arguments."""
    parser = optparse.OptionParser(
        prog='hostreport',
        description='''A standalone tool to generate graph for hosts from
                        ganglia 's rrds.''')
    parser.add_option('--result',
                      metavar='RESULT_DIR',
                      dest='result_dir',
                      default='.',
                      help='result directory to put report files.')
    parser.add_option('--start',
                      metavar='START_TIME',
                      dest='start_time',
                      help='start time of report')
    parser.add_option('--end',
                      metavar='END_TIME',
                      dest='end_time',
                      help='end_time of report')
    parser.add_option('--last-day',
                      action='store_true',
                      dest='last_day',
                      help='generate report for last day')
    parser.add_option('--last-hour',
                      action='store_true',
                      dest='last_hour',
                      help='generate report for last hour')
    parser.add_option('--disk-util-pattern',
                      dest='disk_util_pattern',
                      default='diskstat_(?P<disk>\w+)_percent_io_time',
                      help='a regex to search rrd files for disk utilization')
    parser.add_option('--disk-read-rate-pattern',
                      dest='disk_read_rate_pattern',
                      default='diskstat_(?P<disk>\w+)_read_bytes_per_sec',
                      help='a regex to search rrd files for disk read rate')
    parser.add_option('--disk-write-rate-pattern',
                      dest='disk_write_rate_pattern',
                      default='diskstat_(?P<disk>\w+)_write_bytes_per_sec',
                      help='a regex to search rrd files for disk write rate')
    opts, rrds = parser.parse_args()
    if opts.start_time is not None:
        opts.start_time = datetime.strptime(opts.start_time, '%Y%m%d%H%M%S')
    if opts.end_time is not None:
        opts.end_time = datetime.strptime(opts.end_time, '%Y%m%d%H%M%S')
    opts.rrds = rrds
    return opts


if __name__ == '__main__':
    opts = _parse_args()

    # ensure result directories
    if not path.exists(opts.result_dir):
        os.mkdir(opts.result_dir)

    for host_rrd in opts.rrds:
        print 'Plotting %s' % _extract_hostname(host_rrd)
        plot_disk_util(host_rrd, opts)
        plot_disk_read_rate(host_rrd, opts)
        plot_disk_write_rate(host_rrd, opts)
        plot_cpu(host_rrd, opts)
        plot_mem(host_rrd, opts)
        plot_network(host_rrd, opts)
