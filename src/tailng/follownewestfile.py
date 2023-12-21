#!/usr/bin/env python3

import glob
import os
import sys
from tailng.followfile import FollowFile

class FollowNewestFile:
    def __init__(self, paths, sleep=0.5, quiet=False):
        self.paths = paths
        self.sleep = sleep
        self.quiet = quiet
        self.path = ''
        self.pos = -1
        self.stats = {}
        self.follow_file = None
        self.firstrun = True

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
        for path in self._get_paths(self.paths):
            stat = os.stat(path)
            self.stats[path] = stat
            if stat.st_mtime > mtime:
                mtime = stat.st_mtime
                self.path = path
        if self.firstrun:
            self.pos = self.stats.get(self.path).st_size
        else:
            prevstat = prevstats.get(self.path)
            if prevstat:
                self.pos = prevstat.st_size
            else:
                self.post = 0
        self.firstrun = False

    def get(self):
        prevpath = self.path
        self._find_newest()
        if self.path:
            if self.path != prevpath:
                if not self.quiet:
                    sys.stderr.write(f"Now following: {self.path} from position {self.pos}\n")
                self.follow_file = FollowFile(self.path, self.pos)
            return self.follow_file.get()
        return ''

    def write(self):
        sys.stdout.write(self.get())

    def follow(self):
        import time
        while True:
            self.write()
            time.sleep(self.sleep)


def argParse():
    import argparse
    argParse = argparse.ArgumentParser(description='Like "tail -F", but it always follow the newest file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argParse.add_argument(dest='paths', metavar='PATH', nargs='*', default=['*'], help='Path to follow. Accept file(s), directory or glob')
    args = argParse.parse_args()
    return args

def main():
    try:
        args = argParse()
        follow_newest_file = FollowNewestFile(args.paths)
        follow_newest_file.follow()
        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
