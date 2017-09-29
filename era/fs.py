# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import os.path
import shutil


class FSError(Exception):
    def __init__(self, msg, path=None):
        if path:
            msg = '%s: %s' % (path, msg)
        super(FSError, self).__init__(msg)


class FS(object):
    '''
    This class helps us to wrap normal filesystem calls to allow for
    potential partial "virtualization" of calls
    '''
    def __init__(self, root):
        self.root = root

    def error(self, msg, path):
        path = self.virt_path(path)
        raise FSError(msg, path)

    def virt_path(self, path):
        '''
        Converts a real filesystem path into a virtual path
        '''
        common_prefix = os.path.commonprefix([self.root, path])
        if len(common_prefix) > 1:
            # Cut off the common parts
            path = path[len(common_prefix):]
        else:
            # TODO: Can we now assume it already was a virtual path?
            pass
        return path

    def real_path(self, path):
        '''
        Converts a virtual path into the real filesystem path
        '''
        if len(os.path.commonprefix([self.root, path])) > 1:
            # TODO: Test me!
            return path
        if os.path.isabs(path):
            # TODO: How kosher is this?
            path = path[1:]
        return os.path.join(self.root, path)

    def must_exist(self, path):
        path = self.real_path(path)
        if not self.exists(path):
            self.error('No such file or directory', path)
        return path

    def exists(self, path):
        path = self.real_path(path)
        return os.path.exists(path)

    def isdir(self, path):
        path = self.real_path(path)
        return os.path.isdir(path)

    def isfile(self, path):
        return not self.isdir(path)

    def listdir(self, path):
        path = self.must_exist(path)
        return os.listdir(path)

    def read(self, path):
        path = self.must_exist(path)
        if self.isdir(path):
            self.error('Is a directory', path)
        return open(path, mode='r')

    def write(self, path, append=False):
        path = self.real_path(path)
        if self.isdir(path):
            self.error('Is a directory', path)
        mode = 'a' if append else 'w'
        return open(path, mode)

    def touch(self, path):
        path = self.real_path(path)
        if not self.exists(path):
            open(path, 'a').close()
        else:
            os.utime(path, None)

    def mkdir(self, path):
        path = self.real_path(path)
        if self.exists(path):
            self.error('File exists', path)
        os.mkdir(path)

    def rm(self, path, recursive=False, ignore_errors=False):
        path = self.real_path(path)
        if not ignore_errors:
            self.must_exist(path)
        if self.isdir(path) and not recursive:
            self.error('Is a directory', path)
        elif self.isdir(path):
            shutil.rmtree(path, ignore_errors)
        else:
            os.remove(path)
