# -*- coding: utf-8 -*-
import os.path
import sys

import click

import era
import era.shell

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
CWD = os.path.abspath(os.getcwd())

@click.command('shell', short_help='Runs the 3R4 shell',
        context_settings=CONTEXT_SETTINGS)
@click.argument('root', default=CWD)
@click.version_option(version=era.version, prog_name='3R4')
def shell(root):
    """Starts an 3R4 shell session

    If ROOT is provided, the new session will consider this path to be
    the root of the presented file system. Otherwise, the current
    directory will be used."""
    exit_code = era.shell.start(root)
    sys.exit(exit_code)


def main():
    shell()

def login():
    # TODO: Log the login event!
    main()
