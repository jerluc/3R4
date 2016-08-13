# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import os.path
import time


def expandvars(session, s):
    # Monkey patch new shell environment
    old_env = os.environ.copy()
    os.environ = session.env.as_dict()
    os.environ['?'] = session.last_exit_code

    s = os.path.expandvars(s)

    # Restore old environment
    os.environ = old_env
    return s


def expandpath(session, path):
    # Monkey patch new shell environment
    old_env = os.environ.copy()
    os.environ = session.env.as_dict()

    path = os.path.expanduser(path)

    # Restore old environment
    os.environ = old_env
    return path


def su(session, *args):
    user = args[0] if args else 'root'
    try:
        success = session.changeuser(user)
        if success:
            return 0
        else:
            print('Permission denied (invalid password).')
            return 1
    except: # This should really only catch any Control-c's
        print('')
        return 1


def hostname(session, *_):
    print(session.host)
    return 0


def echo(session, *args):
    msg = ' '.join(args) if args else ''
    print(msg)
    return 0


def env(session, *_):
    for k, v in session.env.items():
        print('%s=%s' % (k, v))
    return 0


def history(session, *_):
    i = 1
    for item in session.history.strings:
        print('%5d %s' % (i, item))
        i += 1
    return 0


def cd(session, *args):
    new_path = args[0] if args else '~'
    if new_path == '-':
        if session.env.get('OLDPWD'):
            new_path = session.env.get('OLDPWD')
        else:
            return 1
    else:
        # Used for passing the '-' parameter
        session.env.set('OLDPWD', session.env.pwd)

    new_path = expandpath(session, new_path)
    path = os.path.abspath(os.path.join(session.env.pwd, new_path))
    session.env.set('PWD', path)
    return 0


def pwd(session, *_):
    print(session.env.pwd)
    return 0


def sleep(session, *args):
    try:
        time.sleep(int(args[0]))
        return 0
    except: # Catch Control-c
        return 130


# TODO: Refactor this to maybe be some kind of mixin?
PATH = {
    'cd': cd,
    'echo': echo,
    'env': env,
    'history': history,
    'hostname': hostname,
    'pwd': pwd,
    'sleep': sleep,
    'su': su
}

