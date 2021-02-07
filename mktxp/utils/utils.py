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


import os, sys, shlex, tempfile, shutil, re
import subprocess, hashlib
from timeit import default_timer
from collections.abc import Iterable
from contextlib import contextmanager
from multiprocessing import Process, Event


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

def get_last_digit_from_shell_cmd(cmd):
    try:
        cmd_output = run_cmd(cmd, shell = True)
    except CmdProcessingError as e:
        if not quiet:
            print ('Error while running cmd: {}'.format(e.args[0]))
        return -1
    else:
        return get_last_digit(cmd_output)

def get_last_digit(str_to_search):
    p = re.compile('(\d*\.?\d+)')
    match = p.search(str_to_search)
    if match:
        return float(match.group())
    else:
        return -1

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


