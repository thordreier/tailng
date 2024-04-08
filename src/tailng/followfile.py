#!/usr/bin/env python3

import os
import sys
from tailng import __version__

class FollowFile:
    """Like "tail -F" """
    # pos=None - follow from end
    # pos=0 - follow from beginning
    # pos=<negateive> - count bytes backward from end
    # pos=<positive> - count bytes from beginning
    def __init__(self, path, pos=None, sleep=0.5, quiet=False):
        self.path = path
        self.sleep = sleep
        self.quiet = quiet
        self.pos = pos
        size = self._getsize()
        if size is None:
            self.pos = None
            self._stderr(f"File {self.path} does not exist")
        else:
            if self.pos is None:
                self.pos = size
            elif self.pos < 0 and -self.pos > size:
                self._stderr(f"Can't seek {self.pos}, starting from beginning of file")
                self.pos = 0
            elif self.pos < 0:
                self.pos = size + self.pos
            elif self.pos > size:
                self._stderr(f"Can't seek {self.pos}, starting from end of file")
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
            return None

    def get(self):
        size = self._getsize()
        if size is None and self.pos is None:
            # File still missing
            return ''
        if size is None and self.pos >= 0:
            self.pos = None
            self._stderr(f"File {self.path} disappeared")
            return ''
        if size >= 0 and self.pos is None:
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
        '-V',
        '--version',
        action = 'version',
        version = __version__,
    )
    parser.add_argument(
        dest = 'path',
        metavar = 'PATH',
        help = 'Path to follow.',
    )
    pos_group = parser.add_mutually_exclusive_group()
    pos_group.add_argument(
        '-w',
        '--whole-file',
        dest = 'whole_file',
        action = 'store_true',
        help = 'Show whole file',
    )
    pos_group.add_argument(
        '-c',
        '--bytes',
        dest = 'pos',
        metavar = 'NUM',
        type = int,
        help = 'Start at byte (accept negative numbers too)',
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
        follow_file = FollowFile(path=args.path, pos=pos)
        follow_file.follow()
        return 0
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
