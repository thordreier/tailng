#!/usr/bin/env python3

import glob
import os
import sys
from tailng import __version__
from tailng.followfile import FollowFile

class FollowNewestFile:
    """Like "tail -F", but it always follow the newest file"""
    # pos=None - follow from end
    # pos=0 - follow from beginning
    # pos=<negateive> - count bytes backward from end
    # pos=<positive> - count bytes from beginning
    def __init__(self, paths, pos=None, sleep=0.5, quiet=False):
        self.paths = paths
        self.start_pos = pos
        self.sleep = sleep
        self.quiet = quiet
        self.path = ''
        self.pos = None
        self.stats = {}
        self.follow_file = None
        self.firstrun = True

    def _stderr(self, msg):
        if not self.quiet:
            sys.stderr.write(msg + "\n")

    @staticmethod
    def _expand_glob(path):
        expanded_paths = []
        for p in glob.glob(path):
            if os.path.isfile(p):
                expanded_paths += [p]
            elif p == path and os.path.isdir(p):
                expanded_paths += FollowNewestFile._expand_glob(p + '/*')
        return expanded_paths

    @staticmethod
    def _get_paths(paths):
        expanded_paths = []
        for p in paths:
            expanded_paths = FollowNewestFile._expand_glob(p)
        uniq_paths = list(set(expanded_paths))
        return uniq_paths

    def _get_pos(self, size, pos):
        if pos is None:
            return size
        elif pos < 0 and -pos > size:
            self._stderr(f"Can't seek {pos}, starting from beginning of file")
            return 0
        elif pos < 0:
            return size + pos
        elif pos > size:
            self._stderr(f"Can't seek {pos}, starting from end of file")
            return size
        return pos

    def _find_newest(self):
        mtime = -1
        prevstats = self.stats
        self.stats = {}
        self.path = ''
        for path in self._get_paths(self.paths):
            stat = os.stat(path)
            self.stats[path] = stat
            if stat.st_mtime > mtime:
                mtime = stat.st_mtime
                self.path = path
        if not self.path:
            if self.firstrun or prevstats:
                self._stderr("No files found")
            self.firstrun = False
            return
        if self.firstrun:
            self.pos = self._get_pos(self.stats.get(self.path).st_size, self.start_pos)
        else:
            prevstat = prevstats.get(self.path)
            if prevstat:
                self.pos = prevstat.st_size
            else:
                self.pos = 0
        self.firstrun = False
        return

    def get(self):
        prevpath = self.path
        self._find_newest()
        if self.path:
            if self.path != prevpath:
                self.follow_file = FollowFile(path=self.path, pos=self.pos, sleep=self.sleep, quiet=self.quiet)
            return self.follow_file.get()
        return ''

    def print(self):
        print(self.get(), end='', flush=True)

    def follow(self):
        import time
        while True:
            self.print()
            time.sleep(self.sleep)


def arg_parse():
    import argparse
    parser = argparse.ArgumentParser(
        description = 'Like "tail -F", but it always follow the newest file',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-V',
        '--version',
        action = 'version',
        version = __version__,
    )
    parser.add_argument(
        dest = 'paths',
        metavar = 'PATH',
        nargs = '*',
        default = ['*'],
        help = 'Path to follow. Accept file(s), directory or glob',
    )
    pos_group = parser.add_mutually_exclusive_group()
    pos_group.add_argument(
        '-w',
        '--whole-file',
        dest = 'whole_file',
        action = 'store_true',
        help = 'Show whole file (only first file opened)',
    )
    pos_group.add_argument(
        '-c',
        '--bytes',
        dest = 'pos',
        metavar = 'NUM',
        type = int,
        help = 'Start at byte (accept negative numbers too) (only first file opened)',
    )
    args = parser.parse_args()
    return args

def main():
    try:
        args = arg_parse()
        if args.whole_file:
            pos = 0
        else:
            pos = args.pos
        follow_newest_file = FollowNewestFile(paths=args.paths, pos=pos)
        follow_newest_file.follow()
        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
