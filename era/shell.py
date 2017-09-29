# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from getpass import getuser, getpass
from socket import gethostname, gethostbyname
from shlex import split as cmd_split

from prompt_toolkit import prompt
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory
from pygments.lexers.shell import BashLexer

from era.commands import PATH, expandvars
from era.env import Env
from era.fs import FS


SHELL_PATH = '/bin/esh'

# TODO: Read this from a config file
DEFAULT_PROMPT_STYLE = style_from_dict({
    # User input
    Token:            '#ffffff',
    # Prompt
    Token.Username:   '#00cc00',
    Token.Path:       '#2200cc',
    # Toolbar
    Token.Toolbar: '#ffffff bg:#333333',
})

ADMIN_PROMPT_STYLE = style_from_dict({
    # User input
    Token:            '#ffffff',
    # Prompt
    Token.Username:   '#cc0000',
    Token.Path:       '#2200cc',
    # Toolbar
    Token.Toolbar: '#ffffff bg:#333333',
})


class ShellSession(object):
    def __init__(self, username, fs, starting_path=None, prompt_style=DEFAULT_PROMPT_STYLE):
        # TODO: Consider rewriting to pass in a fake host/IP
        self.host = gethostname()
        # TODO: Uhhh....wat
        self.ip = gethostbyname(self.host)
        homedir = '/home/%s' % username
        starting_path = starting_path if starting_path else homedir
        self.env = Env(
            SHELL=SHELL_PATH,
            USER=username,
            PWD=starting_path,
            HOME=homedir
        )
        self.fs = fs
        self.manager = KeyBindingManager.for_prompt()
        self.manager.registry.add_binding(Keys.ControlC)(self.on_ctrlc)
        self.prompt_style = prompt_style
        # TODO: Use on-disk history file
        self.history = InMemoryHistory()
        self.is_running = True
        self.last_exit_code = 0
        self.status = 'Welcome back, %s' % username

    # TODO: This can change eventually
    def on_ctrlc(self, event):
        def skip():
            print('')
        event.cli.reset(True)
        event.cli.run_in_terminal(skip)

    def prompt_tokens(self, cli):
        return [
            (Token.Username,   self.env.user),
            (Token.Path,       ' %s $ ' % self.env.display_pwd),
        ]

    # TODO: Should I even use the toolbar?
    def toolbar_tokens(self, cli):
        return [
            (Token.Toolbar, '['),
            (Token.Toolbar, ' '),
            (Token.Toolbar, self.host),
            (Token.Toolbar, '(%s)' % self.ip),
            (Token.Toolbar, ' '),
            (Token.Toolbar, ']'),
        ]

    # TODO: Use the lower-level CLI functionality rather than just the
    # prompt(...) shortcut function
    def prompt(self, msg=None, is_password=False):
        if not msg:
            return prompt(
                key_bindings_registry=self.manager.registry,
                get_prompt_tokens=self.prompt_tokens,
                get_bottom_toolbar_tokens=self.toolbar_tokens,
                style=self.prompt_style,
                history=self.history,
                lexer=BashLexer
            )
        else:
            return prompt(
                msg,
                key_bindings_registry=self.manager.registry,
                get_bottom_toolbar_tokens=self.toolbar_tokens,
                style=self.prompt_style,
                is_password=is_password
            )

    def do_command(self, cmd, *args):
        if cmd == 'exit':
            self.is_running = False
        elif cmd in PATH:
            try:
                self.last_exit_code = PATH[cmd](self, *args)
            except Exception as e:
                print('%s: %s' % (cmd, e))
                self.last_exit_code = 255
        else:
            print('-esh: %s: command not found' % cmd)

    def changeuser(self, user):
        # TODO: Note that we're bypassing prompt_toolkit here because it
        # looks wayyyy too hard to get it to not use '*' for passwords
        password = getpass('Password:')
        if user == 'root':
            if password == 'toor':
                root_session = AdminSession(self)
                root_session.run()
                return True
            else:
                return False
        # TODO: Only start a new session if the user/pass works
        elif True:
            new_session = ShellSession(user)
            new_session.run()
            return True

    def run(self):
        while self.is_running:
            # TODO: Handle malformed commands
            try:
                line = cmd_split(self.prompt())
            except Exception as e:
                print('-esh: %s' % e)
                continue
            line = [expandvars(self, s) for s in line]
            if len(line) > 0:
                cmd = line[0]
                args = line[1:]
                self.do_command(cmd, *args)


class AdminSession(ShellSession):
    def __init__(self, parent, starting_path=None):
        super(self.__class__, self).__init__('root', parent.fs, starting_path=starting_path,
                                             prompt_style=ADMIN_PROMPT_STYLE)

    def prompt_tokens(self, cli):
        return [
            (Token.Username, 'root'),
            (Token.Path,     ' %s # ' % self.env.display_pwd)
        ]


def start(root):
    user = getuser()
    fs = FS(root)
    session = ShellSession(user, fs)
    session.run()
