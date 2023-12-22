#!/usr/bin/env python3

import glob
import os
import sys
from tailng import __version__
from tailng.followfile import FollowFile

class FollowNewestFile:
    """Like "tail -F", but it always follow the newest file"""
    def __init__(self, paths, sleep=0.5, quiet=False):
        self.paths = paths
        self.sleep = sleep
        self.quiet = quiet
        self.path = ''
        self.pos = -1
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
                expanded_paths += FollowNewestFile.expandGlob(p + '/*')
        return expanded_paths

    @staticmethod
    def _get_paths(paths):
        expanded_paths = []
        for p in paths:
            expanded_paths = FollowNewestFile._expand_glob(p)
        uniq_paths = list(set(expanded_paths))
        return uniq_paths

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

            self.pos = self.stats.get(self.path).st_size
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
        '--version',
        '-V',
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
    args = parser.parse_args()
    return args

def main():
    try:
        args = arg_parse()
        follow_newest_file = FollowNewestFile(args.paths)
        follow_newest_file.follow()
        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
