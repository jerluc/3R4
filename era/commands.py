# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from prompt_toolkit import prompt

def sudo(session, *_):
    password = prompt('Password: ', is_password=True)
    if password == 'toor':
        root_session = AdminSession(session.host)
        root_session.run()
    else:
        print('Invalid password!')

COMMANDS = {
    'sudo': sudo
}
