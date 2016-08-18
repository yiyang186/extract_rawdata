# encoding: utf-8

import os
from optparse import OptionParser
import logging
import logging.config
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

class DirNode(object):
    def __init__(self, _path):
        self.data = _path
        if os.path.isdir(_path):
            self.children = [os.path.join(_path, _file) for _file in 
                             os.listdir(_path)]
        else:
            self.children = None

class DirTree(object):

    csv_sizes = [] # 记录所有csv文件的大小
    csv_count = 0
    csv_count_big = 0
    big_limit = 2 ** 20

    def __init__(self, source):
        self.root = self.build_dirtree(source)

    def build_dirtree(self, _path):
        node = DirNode(_path)
        if node.children:
            node.children = [self.build_dirtree(child) for child in 
                             node.children]
        return node

    def get_all_csv_sizes(self):
        self.get_sizes(self.root)

    def get_sizes(self, node):
        if not node.children and os.path.isfile(node.data):
            _path = node.data
            filename, ext  = os.path.splitext(_path)
            if ext == '.CSV':
                size = os.path.getsize(_path)
                DirTree.csv_sizes.append(size)
                DirTree.csv_count += 1
                if size > DirTree.big_limit:
                    DirTree.csv_count_big += 1
                    if DirTree.csv_count_big % 500 == 0:
                    	print DirTree.csv_count, DirTree.csv_count_big
        else:
            for child in node.children:
                self.get_sizes(child) 

if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-s", "--source", dest="src",
                  help="source of files")

    logging.config.fileConfig("logger.conf")
    logger = logging.getLogger("mylogconf01")

    (opts, args) = op.parse_args()

    if os.path.isdir(opts.src):
    	print 'Build tree...'
        dt = DirTree(opts.src)
        print 'Start counting...'
        dt.get_all_csv_sizes()
        print 'Number of csv = ', dt.csv_count
        print 'Number of csv larger than ', dt.big_limit, ' = ', dt.csv_count_big
        sizes = pd.DataFrame(dt.csv_sizes)
        sizes.plot(kind='hist')
        plt.show()
    else:
        logger.error("Wrong directoris!") 