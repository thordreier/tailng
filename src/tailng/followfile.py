#!/usr/bin/env python3

import os
import sys

class FollowFile:
    def __init__(self, path, pos=-1, sleep=0.5):
        self.path = path
        if pos == -1:
            pos = self._getsize()
        self.pos = pos
        self.sleep = sleep

    def _getsize(self):
        return os.path.getsize(self.path)

    def get(self):
        if self.pos == self._getsize():
            return ''
        with open(self.path) as file:
            file.seek(self.pos)
            data = file.read()
            self.pos = file.tell()
            return data

    def write(self):
        sys.stdout.write(self.get())
    
    def follow(self):
        import time
        while True:
            self.write()
            time.sleep(self.sleep)


def arg_parse():
    import argparse
    arg_parse = argparse.ArgumentParser(description='Like "tail -F"', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parse.add_argument(dest='path', metavar='PATH', help='Path to follow.')
    args = arg_parse.parse_args()
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
