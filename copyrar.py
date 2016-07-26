from shutil import copy
import os
from optparse import OptionParser
from decompress import *
from planedata import *  # 该部分不上传

class DirNode(object):
    def __init__(self, _path):
        self.data = _path
        if os.path.isdir(_path):
            self.children = [os.path.join(_path, _file) for _file in 
                             os.listdir(_path)]
        else:
            self.children = None

class DirTree(object):

    # temp是指定的临时文件夹，以'/'结尾，用于临时解压文件
    def __init__(self, source, temp):
        self.root = self.build_dirtree(source)
        self.tempdir = temp

    def build_dirtree(self, _path):
        node = DirNode(_path)
        if node.children:
            node.children = [self.build_dirtree(child) for child in 
                             node.children]
        return node

    def extract_to(self, destination):
        self.dst = destination
        self.traversal(self.root)

    def traversal(self, node):
        if not node.children and os.path.isfile(node.data):
            self.extract(node.data, self.dst)
        else:
            for child in node.children:
                self.traversal(child) 

    def extract(data_path, dst):
        filename, ext = os.path.splitext(data_path)
        if ext == 'zip':
            zfile = ZFile(filename)
            zfile.extract_to(self.tempdir)
        elif: ext == 'rar':
            rfile = RFile(filename)
            rfile.extract_to(self.tempdir)
        elif: ext == 'dat':
            # TODO
        elif: ext in ['lod', 'DAT']:
            # TODO
        else:
            # TODO

    def my_unzip(self, filename):
        z = zipfile.ZipFile(filename, 'r') 
        for f in z.namelist(): 



if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-d", "--destination", dest="dst",
                  help="destination of files")
    op.add_option("-s", "--source", dest="src",
                  help="source of files")
    (opts, args) = op.parse_args()

    if not os.path.exists(opts.dst):
        print "make new directory named", opts.dst
        os.makedirs(opts.dst)

    if os.path.isdir(opts.src) and os.path.isdir(opts.dst):
        dt = DirTree(extract_toopts.src)
        dt.extract_to(opts.dst)
    else:
        print "wrong directoris!"