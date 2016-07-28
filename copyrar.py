# encoding: utf-8

import shutil
import random
import os, sys, re
from optparse import OptionParser
from decompress import *
from planes import *  # 该模块不上传
# import webbrowser

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
    def __init__(self, source, tmp):
        self.root = self.build_dirtree(source)
        self.tempdir = tmp

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

    def extract(self, data_path, dst):
        filename, ext = os.path.splitext(data_path)
        # ext以'.'开头，为'.rar'的样式
        if ext == '.zip':
            zfile = ZFile(data_path)
            zfile.extract_to(self.tempdir)
            dtTmp = DirTree(self.tempdir, self.tempdir)
            dtTmp.extract_to(self.dst)
            self.remove_extracted(data_path)
        elif ext == '.rar':
            rfile = RFile(data_path)
            rfile.extract_to(self.tempdir)
            dtTmp = DirTree(self.tempdir, self.tempdir)
            dtTmp.extract_to(self.dst)
            self.remove_extracted(data_path)
        elif ext in ['.lod', '.DAT', '.dat']:
            path, filename = os.path.split(data_path)
            abspath = self.replace_filename(data_path[4:]) # 只要绝对路径的第4位以后的部分，即不要E:\\
            planenum = self.get_plane_number(abspath)
            _dst = os.path.join(self.dst, planenum)
            if not os.path.exists(_dst):
                os.makedirs(_dst)
            shutil.copy(data_path, _dst)
            print filename
            if len(filename) <= 8:
                new_filename = self.random_filename(filename[: -4], ext, 10)
                new_data_path = os.path.join(_dst, new_filename)
                old_data_path = os.path.join(_dst, filename)
                os.rename(old_data_path, new_data_path)
        else:
            path, filename = os.path.split(data_path)
            print "This is not record file", filename

    # 用于产生length长度文件名，长度不足的用随机字符串补充
    def random_filename(self, filename, ext, length):
        samples = '0123456789abcdefghijklmnopqlmnuvwxyz'
        filename = filename + '-' + ''.join(random.sample(samples, length - len(filename)))
        return filename + ext

    def replace_filename(self, filename):
        return filename.replace('/', '-').replace('\\', '-')

    def get_plane_number(self, filename):
        substrs = filename.split('-')
        substrs = filter(lambda s: len(s) >= 4, substrs)
        substrs = map(lambda s: self.get_substr_for_length(s, 4), substrs)
        substrs = reduce(lambda l1, l2: l1 + l2, substrs)
        substrs = filter(lambda s: not re.search('\D', s), substrs)
        planenum = filter(lambda s: planenums.has_key(s), substrs)
        if len(planenum) > 1:
            print planenum, filename
            return planenum[0]
        if len(planenum) == 0:
            return 'unkown'        # 不清楚机尾号的数据放在unkown目录下
        return planenum[0]

    def get_substr_for_length(self, _str, length):
        # 返回字符串中指定长度的子串
        return [_str[i: i + length] for i in range(len(_str) + 1 - length)]

    def remove_extracted(self, filename):
        path, filename = os.path.split(filename)
        filename, ext = os.path.splitext(filename)
        toberemoved = os.path.join(self.tempdir, filename)
        print toberemoved
        shutil.rmtree(toberemoved)

if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-d", "--destination", dest="dst",
                  help="destination of files")
    op.add_option("-s", "--source", dest="src",
                  help="source of files")
    op.add_option("-t", "--temp_dir", dest="tmp",
                  help="temporary")

    (opts, args) = op.parse_args()

    if not os.path.exists(opts.dst):
        print "make new directory named", opts.dst
        os.makedirs(opts.dst)

    if not os.path.exists(opts.tmp):
        print "make new directory named", opts.tmp
        os.makedirs(opts.tmp)

    if os.path.isdir(opts.src) and os.path.isdir(opts.dst) and os.path.isdir(opts.tmp):
        dt = DirTree(opts.src, opts.tmp)
        dt.extract_to(opts.dst)
    
        # try:
        #     dt = DirTree(opts.src, opts.tmp)
        #     dt.extract_to(opts.dst)
        # except:  
        #     _type, _message, _traceback = sys.exc_info()  
        #     print _type, ":", _message
        #     url = "http://stackoverflow.com/search?q=" + str(info[1])
        #     webbrowser.open_new_tab(url)

    else:
        print "wrong directoris!"