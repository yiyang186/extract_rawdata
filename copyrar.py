# encoding: utf-8

import shutil
import random
import os, sys, re
from optparse import OptionParser
import zipfile
from unrar import rarfile
import logging
import logging.config
from planes import *  # 该模块不上传
 
reload(sys)  
sys.setdefaultencoding('utf8')

class DirNode(object):
    def __init__(self, _path):
        self.data = _path
        if os.path.isdir(_path):
            self.children = [os.path.join(_path, _file) for _file in 
                             os.listdir(_path)]
        else:
            self.children = None

class DirTree(object):

    def __init__(self, source, tmp):
        self.root = self.build_dirtree(source)
        self.tempdir = tmp
        if not os.path.exists(self.tempdir):
            os.makedirs(tmp)

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
        try:
            if 'tmp' not in data_path:
                print data_path
            filename, ext = os.path.splitext(data_path)
            _path, _name = os.path.split(filename)
            # ext以'.'开头，为'.rar'的样式
            if ext == '.zip':
                zfile = zipfile.ZipFile(data_path, 'r')
                unzip_dir = os.path.join(self.tempdir, _name)
                os.makedirs(unzip_dir)
                zfile.extractall(unzip_dir)
                tmp_dir = os.path.join(unzip_dir, 'tmp')
                dtTmp = DirTree(unzip_dir, tmp_dir)
                dtTmp.extract_to(self.dst)
                shutil.rmtree(unzip_dir)
            elif ext == '.rar':
                rfile = rarfile.RarFile(data_path, 'r')
                unrar_dir = os.path.join(self.tempdir, _name)
                os.makedirs(unrar_dir)
                rfile.extractall(unrar_dir)
                tmp_dir = os.path.join(unrar_dir, 'tmp')
                dtTmp = DirTree(unrar_dir, tmp_dir)
                dtTmp.extract_to(self.dst)
                shutil.rmtree(unrar_dir)
            elif ext in ['.lod', '.DAT', '.dat']:
                path, filename = os.path.split(data_path)
                abspath = self.replace_filename(data_path[4:]) # 只要绝对路径的第4位以后的部分，即不要E:\\
                planenum = self.get_plane_number(abspath)
                _dst = os.path.join(self.dst, planenum)
                if not os.path.exists(_dst):
                    os.makedirs(_dst)
                shutil.copy(data_path, _dst)
                if len(filename) <= 8:
                    new_filename = self.random_filename(filename[: -4], ext, 12)
                    new_data_path = os.path.join(_dst, new_filename)
                    old_data_path = os.path.join(_dst, filename)
                    os.rename(old_data_path, new_data_path)
            else:
                path, filename = os.path.split(data_path)
        except:
            info = sys.exc_info()
            logger.error("data path: " + data_path)
            logger.error(str(info[0]) + ":" + str(info[1]))
            _dst = os.path.join(dst, 'unkown')
            if not os.path.exists(_dst):
                os.makedirs(_dst)
            shutil.copy(data_path, _dst)
            try:
                shutil.rmtree(self.tempdir)
            except:
                info = sys.exc_info()
                logger.error(str(info[0]) + ":" + str(info[1]))


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
        planenum = set(planenum)
        if len(planenum) > 1:
            logger.info(filename)
            logger.info("Get more than one flight number")
        if len(planenum) == 0:
            return 'unkown'        # 不清楚机尾号的数据放在unkown目录下
        return planenum.pop()

    def get_substr_for_length(self, _str, length):
        # 返回字符串中指定长度的子串
        return [_str[i: i + length] for i in range(len(_str) + 1 - length)]

if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-d", "--destination", dest="dst",
                  help="destination of files")
    op.add_option("-s", "--source", dest="src",
                  help="source of files")
    op.add_option("-t", "--temp_dir", dest="tmp",
                  help="temporary")

    logging.config.fileConfig("logger.conf")
    logger = logging.getLogger("mylogconf01")

    (opts, args) = op.parse_args()

    if not os.path.exists(opts.dst):
        print "Make new directory named " + opts.dst
        os.makedirs(opts.dst)

    if os.path.isdir(opts.src) and os.path.isdir(opts.dst):
        dt = DirTree(opts.src, opts.tmp)
        dt.extract_to(opts.dst)
    else:
        logger.error("Wrong directoris!") 