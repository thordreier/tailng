#!/usr/bin/env python3

import os
import sys
from tailng import __version__

class FollowFile:
    """Like "tail -F" """
    def __init__(self, path, pos=-1, sleep=0.5, quiet=False):
        self.path = path
        self.sleep = sleep
        self.quiet = quiet
        self.pos = pos
        size = self._getsize()
        if size < 0:
            self.pos = -1
            self._stderr(f"File {self.path} does not exist")
        else:
            if self.pos == -1:
                self.pos = size
            self._stderrpos()

    def _stderr(self, msg):
        if not self.quiet:
            sys.stderr.write(msg + "\n")

    def _stderrpos(self):
        self._stderr(f"Now following {self.path} from position {self.pos}")

    def _getsize(self):
        try:
            return os.path.getsize(self.path)
        except FileNotFoundError:
            return -1

    def get(self):
        size = self._getsize()
        if size < 0 and self.pos < 0:
            # File still missing
            return ''
        if size < 0 and self.pos >= 0:
            self.pos = -1
            self._stderr(f"File {self.path} disappeared")
            return ''
        if size >= 0 and self.pos < 0:
            self.pos = 0
            self._stderr(f"File {self.path} created")
            self._stderrpos()
        if self.pos == size:
            return ''
        if self.pos > size:
            self.pos = size
            self._stderr(f"File {self.path} shrinked")
            self._stderrpos()
            return ''
        with open(self.path) as file:
            file.seek(self.pos)
            data = file.read()
            self.pos = file.tell()
            return data

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
        description = 'Like "tail -F"',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--version',
        '-V',
        action = 'version',
        version = __version__,
    )
    parser.add_argument(
        dest = 'path',
        metavar = 'PATH',
        help = 'Path to follow.',
    )
    args = parser.parse_args()
    return args

def main():
    try:
        args = arg_parse()
        follow_file = FollowFile(args.path)
        follow_file.follow()
        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
