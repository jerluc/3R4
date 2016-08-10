# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from getpass import getuser, getpass
from socket import gethostname
from shlex import split as cmd_split

from prompt_toolkit import prompt
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory
from pygments.lexers.shell import BashLexer

from era.env import Env


SHELL_PATH = '/bin/esh'

# TODO: Read this from a config file
DEFAULT_PROMPT_STYLE = style_from_dict({
    # User input
    Token:            '#ffffff',
    # Prompt
    Token.Username:   '#00cc00',
    Token.Path:       '#2200cc',
    Token.DollarSign: '#ffffff',
    # Toolbar
    Token.Toolbar: '#ffffff bg:#333333',
})


ADMIN_PROMPT_STYLE = style_from_dict({
    # User input
    Token:            '#ffffff',
    # Prompt
    Token.Path:       '#cc0000',
    Token.Hash:       '#cc0000',
    # Toolbar
    Token.Toolbar: '#ffffff bg:#333333',
})


def sudo(session, *_):
    # TODO: Note that we're bypassing prompt_toolkit here because it
    # looks wayyyy too hard to get it to not use '*' for passwords
    try:
        password = getpass('Password:')
        if password == 'toor':
            root_session = AdminSession(session.host)
            root_session.run()
        else:
            print('Invalid password!')
    except: # This should really only catch any Control-c's
        print('')


def env(session, *_):
    for k, v in session.env.items():
        print('%s=%s' % (k, v))


def history(session, *_):
    i = 1
    for item in session.history.strings:
        print('%5d %s' % (i, item))
        i += 1


# TODO: Refactor this to maybe be some kind of mixin?
COMMANDS = {
    'env': env,
    'history': history,
    'sudo': sudo
}


class ShellSession(object):
    def __init__(self, username, host, starting_path=None,
            prompt_style=DEFAULT_PROMPT_STYLE):
        self.host = host
        homedir = '/home/%s' % username
        self.env = Env(
            SHELL=SHELL_PATH,
            USER=username,
            PWD=starting_path if starting_path else homedir,
            HOME=homedir
        )
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
            (Token.Path,       ' ' + self.env.display_pwd),
            (Token.DollarSign, ' $ '),
        ]

    def toolbar_tokens(self, cli):
        return [
            (Token.Toolbar, self.status)
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
        elif cmd in COMMANDS:
            COMMANDS[cmd](self, *args)
        else:
            print('-esh: %s: command not found' % cmd)

    def run(self):
        while self.is_running:
            line = cmd_split(self.prompt())
            if len(line) > 0:
                cmd = line[0]
                args = line[1:]
                self.do_command(cmd, *args)


class AdminSession(ShellSession):
    def __init__(self, host, starting_path=None):
        super(self.__class__, self).__init__('root', host,
                starting_path=starting_path,
                prompt_style=ADMIN_PROMPT_STYLE)

    def prompt_tokens(self, cli):
        return [
            (Token.Path,       self.env.display_pwd),
            (Token.Hash, ' # '),
        ]


def start(root):
    user = getuser()
    host = gethostname()
    session = ShellSession(user, host)
    session.run()

