# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import os
import os.path
import sys
import time


# Note that this gets filled in by using the @command decorator
PATH = {}


def command(f):
    PATH[f.__name__] = f
    return f


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
    path = os.path.abspath(os.path.join(session.env.pwd, path))

    # Restore old environment
    os.environ = old_env
    return path


@command
def su(session, *args):
    '''Change user'''
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


@command
def hostname(session, *_):
    '''Prints the current hostname'''
    print(session.host)
    return 0


@command
def echo(session, *args):
    '''Prints a message'''
    msg = ' '.join(args) if args else ''
    print(msg)
    return 0


@command
def env(session, *_):
    '''Prints the environment variables'''
    for k, v in session.env.items():
        print('%s=%s' % (k, v))
    return 0


@command
def history(session, *_):
    '''Prints the command history'''
    i = 1
    for item in session.history.strings:
        print('%5d %s' % (i, item))
        i += 1
    return 0


@command
def cd(session, *args):
    '''Changes current directory'''
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
    session.fs.must_exist(new_path)
    session.env.set('PWD', new_path)
    return 0


@command
def pwd(session, *_):
    '''Prints the current directory'''
    print(session.env.pwd)
    return 0


@command
def ls(session, *args):
    '''Lists the contents of a directory'''
    path = args[0] if args else session.env.pwd
    path = expandpath(session, path)
    for f in session.fs.listdir(path):
        print(f)
    return 0


@command
def mkdir(session, *args):
    '''Creates a new directory'''
    path = expandpath(session, args[0])
    session.fs.mkdir(path)
    return 0


@command
def touch(session, *args):
    '''Creates a new file'''
    path = expandpath(session, args[0])
    session.fs.touch(path)
    return 0


@command
def rm(session, *args):
    '''Removes a file or directory'''
    # TODO: This is horribly wrong!
    flags = []
    for a in args:
        if not a.startswith('-'):
            break
        flags.append(a)
    args = args[len(flags):]
    flags = ''.join(flags).replace('-', '')
    path = expandpath(session, args[0])
    recursive = 'r' in flags
    ignore_errors = 'f' in flags
    session.fs.rm(path, recursive, ignore_errors)
    return 0


@command
def cat(session, *args):
    '''Concatenate and print files'''
    for path in args:
        path = expandpath(session, path)
        with session.fs.read(path) as f:
            for l in f:
                print(l[:-1])
    return 0


@command
def sleep(session, *args):
    '''Suspend execution for an interval of time'''
    try:
        time.sleep(int(args[0]))
        return 0
    except: # Catch Control-c
        return 130


@command
def help(session, *_):
    '''Prints a list of available shell commands'''
    print('')
    print('Available shell commands:\n')

    cmds = sorted(PATH.keys())
    max_cmd_width = max([len(c) for c in cmds])
    template = '\033[1m%' + str(max_cmd_width) + 's\033[0m %s'
    for cmd in cmds:
        desc = PATH[cmd].__doc__
        print(template % (cmd, desc))
    print('')
    return 0

