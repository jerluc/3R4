# -*- coding: utf-8 -*-
class Env(object):
    def __init__(self, **kwargs):
        self.env = kwargs.copy()

    def get(self, key, default=''):
        return self.env.get(key, default)

    def set(self, key, value):
        self.env[key] = value

    @property
    def shell(self):
        return self.env['SHELL']

    @property
    def display_pwd(self):
        return '~' if self.pwd == self.home else self.pwd

    @property
    def pwd(self):
        return self.env['PWD']

    @property
    def user(self):
        return self.env['USER']

    @property
    def home(self):
        return self.env['HOME']

    @property
    def path(self):
        return self.get('PATH', '')

    def items(self):
        return self.env.items()

    def as_dict(self):
        return self.env.copy()
