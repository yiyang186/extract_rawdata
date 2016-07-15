from shutil import copy
import os
from optparse import OptionParser

class DirNode(object):
    def __init__(self, _path):
        self.data = _path
        if os.path.isdir(_path):
            self.children = [os.path.join(_path, _file) for _file in os.listdir(_path)]
        else:
            self.children = None

class DirTree(object):

    def __init__(self, source):
        self.root = self.build_dirtree(source)

    def build_dirtree(self, _path):
        node = DirNode(_path)
        if node.children:
            node.children = [self.build_dirtree(child) for child in node.children]
        return node

    def copy(self, destination):
        self.dst = destination
        self.copy_files(self.root)

    def copy_files(self, node):
        if not node.children and os.path.isfile(node.data):
            copy(node.data, self.dst)
        else:
            for child in node.children:
                self.copy_files(child) 

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
        dt = DirTree(opts.src)
        dt.copy(opts.dst)
    else:
        print "wrong directoris!"