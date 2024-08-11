# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from functools import lru_cache
import os, sys, shlex, tempfile, shutil, re
import subprocess, hashlib, urllib
import time
from timeit import default_timer
from collections.abc import Iterable
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from multiprocessing import Process, Event
from datetime import timedelta
from packaging.version import parse

''' Utilities / Helpers
'''
@contextmanager
def temp_dir(quiet = True):
    ''' Temp dir context manager
    '''
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        # remove tmp dir
        try:
            shutil.rmtree(tmp_dir)
        except OSError as e:
            if not quiet:
                print ('Error while removing a tmp dir: {}'.format(e.args[0]))

class CmdProcessingError(Exception):
    pass

def run_cmd(cmd, shell = False, quiet = False):
    ''' Runs shell commands in a separate process
    '''
    if not shell:
        cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = shell)
    output = proc.communicate()[0].decode('utf-8')
    if proc.returncode != 0 and not quiet:
        raise CmdProcessingError(output)
    return output

def parse_mkt_uptime(time):
    time_dict = re.match(r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?', time).groupdict()
    delta = timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds() 
    return int(delta) if delta else 0

def str2bool(str_value, default = None):
    if not str_value or not type(str_value) is str:
        return False
    str_value = str_value.lower()
    if str_value in ('y', 'yes', 't', 'true', 'on', 'ok', '1'):
        return True
    elif str_value in ('n', 'no', 'f', 'false', 'off', 'fail', '0'):
        return False
    elif default is not None:
        return default
    else:
        raise ValueError(f'Invalid truth value: {str_value}')
        
class FSHelper:
    ''' File System ops helper
    '''
    @staticmethod
    def full_path(path, check_parent_path = False):
        ''' Full path
        '''
        if path:
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            path = os.path.abspath(path)
            path = os.path.realpath(path)

        # for files, check that the parent dir exists
        if check_parent_path:
            if not os.access(os.path.dirname(path), os.W_OK):
                print('Non-valid folder path:\n\t "{}"'.format(os.path.dirname(path)))
                sys.exit(1)

        return path if path else None

    @staticmethod
    def mountpoint(path):
        ''' The mount point portion of a path
        '''
        path = FSHelper.full_path(path)
        while path != os.path.sep:
            if os.path.ismount(path):
                return path
            path = os.path.realpath(os.path.join(path, os.pardir))
        return path if path != os.path.sep else None

    @staticmethod
    def move_FS_entry(orig_path, target_path,
                      check_unique = True,
                      quiet = False, stop = False):
        ''' Moves FS entry
        '''
        succeeded = False
        try:
            if check_unique and os.path.exists(target_path):
                raise OSError('\nTarget path entry already exists')
            shutil.move(orig_path, target_path)
            succeeded = True
        except OSError as e:
            if not quiet:
                print(str(e))
                print('Failed to move entry:\n\t{0}\n\t{1}'.format(orig_path, target_path))
                print('Exiting...') if stop else print('Skipping...')
            if stop:
                sys.exit(1)
        return succeeded

    @staticmethod
    def file_md5(fpath, block_size=0, hex=False):
        ''' Calculates MD5 hash for a file at fpath
        '''
        md5 = hashlib.md5()
        if block_size == 0:
            block_size = 128 * md5.block_size
        with open(fpath,'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                md5.update(chunk)
        return md5.hexdigest() if hex else md5.digest()


class UniqueDirNamesChecker:
    ''' Unique file names Helper
    '''
    def __init__(self, src_dir, unique_fnames = None):
        self._uname_gen = unique_fnames() if unique_fnames else self.unique_fnames()

        # init the generator function with file names from given source directory
        src_dir = FSHelper.full_path(src_dir)
        fnames = [fname for fname in os.listdir(src_dir)]

        for fname in fnames:
            next(self._uname_gen)
            self._uname_gen.send(fname)

    def unique_name(self, fname):
        ''' Returns unique file name
        '''
        next(self._uname_gen)
        return self._uname_gen.send(fname)

    @staticmethod
    def unique_fnames():
        ''' default unique file names generator method,
            via appending a simple numbering pattern
        '''
        unique_names = {}
        while True:
            fname = yield
            while True:
                if fname in unique_names:
                    unique_names[fname] += 1
                    name_base, name_ext = os.path.splitext(fname)
                    fname = '{0}_{1}{2}'.format(name_base, unique_names[fname], name_ext)
                else:
                    unique_names[fname] = 0
                    yield fname
                    break


class UniquePartialMatchList(list):
    ''' Enables matching elements by unique "shortcuts"
        e.g:
            >> 'Another' in UniquePartialMatchList(['A long string', 'Another longs string'])
            >> True
            >>'long' in UniquePartialMatchList(['A long string', 'Another longs string'])
            >> False
            >> l.find('Another')
            >> 'Another longs string'
    '''
    def _matched_items(self, partialMatch):
        ''' Generator expression of <matched items>, where <matched item> is
            a tuple of (<matched_element>, <is_exact_match>)
        '''
        def _contains_or_equal(item):
            if isinstance(item, Iterable):
                return (partialMatch in item)
            else:
                return (partialMatch == item)
        return ((item, (partialMatch == item)) for item in self if _contains_or_equal(item))

    def find(self, partialMatch):
        ''' Returns the element in which <partialMatch> can be found
            <partialMatch> is found if it either:
                equals to an element or is contained by exactly one element
        '''
        matched_cnt, unique_match = 0, None
        matched_items = self._matched_items(partialMatch)
        for match, exact_match in matched_items:
            if exact_match:
                # found exact match
                return match
            else:
                # found a partial match
                if not unique_match:
                    unique_match = match
                matched_cnt += 1
        return unique_match if matched_cnt == 1 else None

    def __contains__(self, partialMatch):
        ''' Check if <partialMatch> is contained by an element in the list,
            where <contained> is defined either as:
                either "equals to element" or "contained by exactly one element"
        '''
        return True if self.find(partialMatch) else False


class RepeatableTimer:
    def __init__(self, interval, func, args=[], kwargs={}, process_name = None, repeatable = True, restartable = False):
        self.process_name = process_name
        self.interval = interval
        self.restartable = restartable
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
        self.finished = Event()
        self.run_once = Event()
        if not repeatable:
            self.run_once.set()            
        self.process = Process(name = self.process_name, target=self._execute)

    def start(self):
        if self.restartable:
            self.finished.clear()
            self.process = Process(name = self.process_name, target=self._execute, daemon=True)
        self.process.start()

    def stop(self):
        self.finished.set()
        if self.process.is_alive:
            self.process.join()

    def _execute(self):
        while True:
            self.func(*self.args, **self.kwargs)
            if self.finished.is_set() or self.run_once.is_set():
                break
            self.finished.wait(self.interval)     

class Benchmark:
    def __enter__(self):
        self.start = default_timer()
        return self

    def __exit__(self, *args):
        self.time = default_timer() - self.start


# mapping of channels to RSS feeds
CHANNEL_RSS_FEED_MAPPING = {
    'development': 'https://mikrotik.com/development.rss',
    'long-term': 'https://mikrotik.com/bugfix.rss',
    'stable': 'https://mikrotik.com/current.rss',
    'testing': 'https://mikrotik.com/candidate.rss',
}


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


@lru_cache(maxsize=5)
def get_available_updates(channel, ttl_hash=get_ttl_hash()):
    """Check the RSS feed for available updates for a given update channel.
    This method fetches the RSS feed and returns all version from the parsed XML.
    Version numbers are parsed into version.Version instances (part of setuptools)."""
    del ttl_hash
    rss_feed = CHANNEL_RSS_FEED_MAPPING[channel]

    print(f'Fetching available ROS releases from {rss_feed}')
    versions = []
    with urllib.request.urlopen(rss_feed) as response:
        result = response.read()
        root = ET.fromstring(result)
        channel = root[0]

        for child in channel:
            # iterate over all updates
            if child.tag == 'item':
                title = child[0]
                # extract and parse the version number from title
                version_text = re.findall(r'[\d+\.]+', title.text)[0]
                version_number = parse(version_text)
                versions.append(version_number)
    return versions


def parse_ros_version(string):
    """Parse the version returned from the /system/resource command.
    Returns a tuple: (<version>, <channel>).

    >>> parse_ros_version('1.2.3 (stable)')
    1.2.3, stable
    """
    version, channel = re.findall(r'([\d\.]+).*?([\w]+)', string)[0]
    return parse(version), channel

def builtin_wifi_capsman_version(version):
    """Try to check if the version is Wifi version of RouterOS (>= 7.13).
    Returns a boolean"""
    try:
        cur_version, _ = parse_ros_version(version)
        if cur_version >= parse('7.13'):
            return True
    except Exception as err:
        print(f'could not get current RouterOS version, because: {err}')
    return False

def routerOS7_version(version):
    try:
        cur_version, _ = parse_ros_version(version)
        if cur_version >= parse('7.0'):
            return True
    except Exception as err:
        print(f'could not get current RouterOS version, because: {err}')
    return False

def check_for_updates(cur_version):
    """Try to check if there is a newer version available.
    If anything goes wrong, it returns the same version.
    Returns a tuple: (<current version>, <newest version>)"""
    error = False
    try:
        cur_version, channel = parse_ros_version(cur_version)
        available_versions = get_available_updates(channel)
        newest_version = sorted(available_versions)[-1]
    except KeyError:
        print(f'unknown update channel {channel}')
        error = True
    except urllib.error.HTTPError as err:
        print(f'update feed returned: {err}')
        error = True
    except Exception as err:
        print(f'could not check for updates, because: {err}')
        error = True

    if error:
        return cur_version, cur_version

    return cur_version, newest_version
