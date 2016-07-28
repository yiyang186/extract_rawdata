# encoding: utf-8

import zipfile
from unrar import rarfile
import os

class ZFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def __addfile(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.__addfile(*path)
            else:
                self.__addfile(path)
        self.zfile.close()

    def extract_to(self, path):
        for f in self.zfile.namelist():
            self.__extract(f, path)

    def __extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            file(f, 'wb').write(self.zfile.read(filename))
        self.zfile.close()

class RFile(object):

    # 目前unrar这个库只允许'r'模式
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.rfile = rarfile.RarFile(filename, mode)

    def extract_to(self, path):
        self.rfile.extractall(path)
        # for f in self.rfile.namelist():
        #     self.__extract(f, path)

    def __extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            _dir = os.path.dirname(f)
            if not os.path.exists(_dir):
                os.makedirs(_dir)
            file(f, 'wb').write(self.rfile.open(filename))
        self.rfile.close()