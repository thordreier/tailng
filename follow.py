#!/usr/bin/env python3


import argparse
import glob
import os
import sys
import time


class FollowFile:

    def __init__(self, filePath, fileSeek=-1):
        self.filePath = filePath
        if fileSeek == -1:
            fileSeek = self.getFileSize()
        self.fileSeek = fileSeek
        return

    def getFileSize(self):
        return os.path.getsize(self.filePath)

    def getRest(self):
        if self.fileSeek == self.getFileSize():
            return
        file = open(self.filePath)
        file.seek(self.fileSeek)
        print(file.read(), end='')
        self.fileSeek = file.tell()
        file.close()
        return


class FollowNewestFile:

    stats = {}
    path = ''
    seek = -1
    followFile = None
    firstRun = True

    def __init__(self, paths):
        self.paths = paths

    def expandGlob(self, path):
        paths = []
        for p in glob.glob(path):
            if os.path.isfile(p):
                paths += [p]
            elif p == path and os.path.isdir(p):
                paths += self.expandGlob(p + '/*')
        return paths

    def getPaths(self):
        paths = []
        for path in self.paths:
            paths = self.expandGlob(path)
        paths = list(set(paths))
        return paths

    def findNewestPath(self):
        mtime = -1
        lastStats = self.stats
        self.stats = {}
        for path in self.getPaths():
            stat = os.stat(path)
            self.stats[path] = stat
            if stat.st_mtime > mtime:
                mtime = stat.st_mtime
                self.path = path
        if self.firstRun:
            self.seek = self.stats.get(self.path).st_size
        else:
            lastStat = lastStats.get(self.path)
            if lastStat:
                self.seek = lastStat.st_size
            else:
                self.seek = 0
        self.firstRun = False

    def runOnce(self):
        lastPath = self.path
        self.findNewestPath()
        if self.path:
            if self.path != lastPath:
                print("Now following: {} from {}".format(self.path, self.seek), file=sys.stderr)
                self.followFile = FollowFile(self.path, self.seek)
            self.followFile.getRest()

    def run(self):
        while True:
            self.runOnce()
            time.sleep(0.5)


def argParse():
    argParse = argparse.ArgumentParser(description='Like "tail -F", but it always follow the newest file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argParse.add_argument(dest='paths', metavar='PATH', nargs='*', default=['*'], help='Path to follow. Accept file(s), directory or glob')
    args = argParse.parse_args()
    return args


def main():
    try:
        args = argParse()
        followNewestFile = FollowNewestFile(args.paths)
        followNewestFile.run()
        return 0
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    sys.exit(main())
